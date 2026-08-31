package com.Project.LearningManagementSystem.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * FileController exposes two public endpoints for serving uploaded files:
 *
 *   GET /files/download  – triggers a browser "Save As" dialog (Content-Disposition: attachment).
 *                          In Swagger UI the "Download file" button appears above the raw response body.
 *   GET /files/view      – renders the file inline (Content-Disposition: inline) so browsers
 *                          open it directly (e.g. PDF viewer, image).
 *
 * Both endpoints accept a {@code path} query parameter whose value must start with "/uploads/"
 * (exactly the value stored in the database by FileUploadUtil, e.g.
 *  /uploads/resources/abc123_slides.pdf  or  /uploads/assignments/xyz_submission.pdf).
 *
 * Security: both endpoints are permit-all in SecurityConfig so they can be exercised from
 * Swagger UI without a JWT token.
 */
@RestController
@RequestMapping("/files")
@Tag(name = "Files", description = "Download or view uploaded files (PDFs, DOCX, etc.)")
public class FileController {

    @Value("${app.upload.dir:./uploads}")
    private String uploadDir;

    // ------------------------------------------------------------------ //
    //  DOWNLOAD  (Content-Disposition: attachment)                         //
    // ------------------------------------------------------------------ //

    @Operation(
        summary = "Download a file",
        description = "Returns the file as an **attachment**.\n\n"
            + "In Swagger UI, after executing this endpoint, click the **Download file** button "
            + "that appears right above the `%PDF-1.7` stream in the response body. "
            + "This saves the file to your computer so you can open it in Chrome, Edge, or Adobe Reader.\n\n"
            + "**How to get the `path`:** call any endpoint that returns `resource_url` or `file_url` "
            + "(e.g. GET /lessons/{id}) and copy-paste the value here, "
            + "e.g. `/uploads/resources/abc123_lecture.pdf`."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "File returned as attachment",
            content = @Content(mediaType = "application/octet-stream")),
        @ApiResponse(responseCode = "400", description = "Invalid or unsafe path supplied"),
        @ApiResponse(responseCode = "404", description = "File not found on server")
    })
    @GetMapping("/download")
    public ResponseEntity<Resource> downloadFile(
        @Parameter(
            description = "Relative file path as stored in DB — must start with /uploads/, "
                + "e.g. `/uploads/resources/abc123_lecture.pdf`",
            example = "/uploads/resources/abc123_lecture.pdf",
            required = true
        )
        @RequestParam("path") String relativePath
    ) {
        return serveFile(relativePath, false);
    }

    // ------------------------------------------------------------------ //
    //  VIEW  (Content-Disposition: inline)                                  //
    // ------------------------------------------------------------------ //

    @Operation(
        summary = "View / preview a file inline",
        description = "Returns the file with **Content-Disposition: inline** so the browser "
            + "(or Swagger UI response pane) renders it directly — PDFs open in the built-in viewer, "
            + "images are displayed, etc.\n\n"
            + "**How to get the `path`:** copy the `resource_url` or `file_url` value returned by "
            + "any resource/submission endpoint, e.g. `/uploads/resources/abc123_lecture.pdf`."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "File returned for inline viewing",
            content = @Content(mediaType = "application/pdf")),
        @ApiResponse(responseCode = "400", description = "Invalid or unsafe path supplied"),
        @ApiResponse(responseCode = "404", description = "File not found on server")
    })
    @GetMapping("/view")
    public ResponseEntity<Resource> viewFile(
        @Parameter(
            description = "Relative file path as stored in DB — must start with /uploads/, "
                + "e.g. `/uploads/resources/abc123_lecture.pdf`",
            example = "/uploads/resources/abc123_lecture.pdf",
            required = true
        )
        @RequestParam("path") String relativePath
    ) {
        return serveFile(relativePath, true);
    }

    // ------------------------------------------------------------------ //
    //  Shared helper                                                        //
    // ------------------------------------------------------------------ //

    /**
     * Resolves the stored relative path to an actual file on disk and returns the response.
     *
     * @param relativePath the path as stored in DB (must start with "/uploads/")
     * @param inline       true  → Content-Disposition: inline  (view in browser)
     *                     false → Content-Disposition: attachment (force download)
     */
    private ResponseEntity<Resource> serveFile(String relativePath, boolean inline) {

        // Security guard: only allow paths under /uploads/
        if (relativePath == null || !relativePath.startsWith("/uploads/")) {
            throw new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "Path must start with /uploads/ — supply the exact value returned by the API, "
                    + "e.g. /uploads/resources/abc123_lecture.pdf"
            );
        }

        // Strip the leading "/uploads/" prefix to resolve against the upload root directory
        String subPath = relativePath.substring("/uploads/".length());

        Path filePath;
        try {
            Path uploadRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
            filePath = uploadRoot.resolve(subPath).normalize();

            // Path-traversal guard: resolved path must remain inside the upload root
            if (!filePath.startsWith(uploadRoot)) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid file path.");
            }
        } catch (ResponseStatusException rse) {
            throw rse;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid file path.");
        }

        if (!Files.exists(filePath) || !Files.isRegularFile(filePath)) {
            throw new ResponseStatusException(
                HttpStatus.NOT_FOUND,
                "File not found on server: " + relativePath
            );
        }

        Resource resource;
        try {
            resource = new UrlResource(filePath.toUri());
        } catch (IOException e) {
            throw new ResponseStatusException(
                HttpStatus.INTERNAL_SERVER_ERROR,
                "Could not read file: " + e.getMessage()
            );
        }

        // Detect MIME type for a correct Content-Type header
        String contentType = detectContentType(filePath);

        // Build RFC 5987-compliant Content-Disposition header
        String filename = filePath.getFileName().toString();
        String encodedFilename = URLEncoder.encode(filename, StandardCharsets.UTF_8)
                                           .replace("+", "%20");
        String disposition = inline
            ? "inline; filename=\"" + filename + "\"; filename*=UTF-8''" + encodedFilename
            : "attachment; filename=\"" + filename + "\"; filename*=UTF-8''" + encodedFilename;

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(contentType))
            .header(HttpHeaders.CONTENT_DISPOSITION, disposition)
            .body(resource);
    }

    /** Detects MIME type with extension-based fallbacks for common document formats. */
    private String detectContentType(Path path) {
        try {
            String detected = Files.probeContentType(path);
            if (detected != null && !detected.isBlank()) {
                return detected;
            }
        } catch (IOException ignored) {
            // fall through to extension-based detection
        }

        String name = path.getFileName().toString().toLowerCase();
        if (name.endsWith(".pdf"))  return "application/pdf";
        if (name.endsWith(".docx")) return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
        if (name.endsWith(".doc"))  return "application/msword";
        if (name.endsWith(".pptx")) return "application/vnd.openxmlformats-officedocument.presentationml.presentation";
        if (name.endsWith(".ppt"))  return "application/vnd.ms-powerpoint";
        if (name.endsWith(".txt"))  return "text/plain";
        if (name.endsWith(".zip"))  return "application/zip";
        if (name.endsWith(".png"))  return "image/png";
        if (name.endsWith(".jpg") || name.endsWith(".jpeg")) return "image/jpeg";

        return "application/octet-stream"; // safe default — always triggers a download
    }
}
