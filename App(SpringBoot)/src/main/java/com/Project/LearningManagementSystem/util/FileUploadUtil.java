package com.Project.LearningManagementSystem.util;

import com.Project.LearningManagementSystem.exception.BadRequestException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

@Component
public class FileUploadUtil {

    @Value("${app.upload.dir:./uploads}")
    private String uploadDir;

    private static final long MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15 MB
    private static final Set<String> ALLOWED_DOCUMENT_EXTENSIONS = Set.of(
            ".pdf", ".doc", ".docx", ".txt", ".zip", ".ppt", ".pptx");

    public String sanitizeFilename(String filename) {
        if (filename == null)
            return "file";
        String clean = filename.replaceAll("[^a-zA-Z0-9_.-]", "_");
        clean = clean.replaceAll("^[._]+|[._]+$", "");
        return clean.isEmpty() ? "file" : clean;
    }

    public String saveUploadedFile(MultipartFile file, String subfolder) {
        return saveUploadedFile(file, subfolder, ALLOWED_DOCUMENT_EXTENSIONS, MAX_FILE_SIZE_BYTES);
    }

    public String saveUploadedFile(MultipartFile file, String subfolder, Set<String> allowedExtensions, long maxSize) {
        if (file == null || file.isEmpty() || file.getOriginalFilename() == null) {
            throw new BadRequestException("Uploaded file must have a valid filename and non-empty content");
        }

        String originalName = file.getOriginalFilename();
        int dotIndex = originalName.lastIndexOf('.');
        if (dotIndex == -1) {
            throw new BadRequestException("File must have a valid extension");
        }
        String ext = originalName.substring(dotIndex).toLowerCase();
        if (!allowedExtensions.contains(ext)) {
            throw new BadRequestException(
                    "File extension '" + ext + "' is not supported. Allowed: " + allowedExtensions);
        }

        if (file.getSize() > maxSize) {
            throw new BadRequestException(
                    "File size exceeds maximum allowed limit of " + (maxSize / (1024 * 1024)) + "MB");
        }

        try {
            Path targetDir = Paths.get(uploadDir, subfolder).toAbsolutePath().normalize();
            Files.createDirectories(targetDir);

            String cleanName = sanitizeFilename(originalName);
            String uniqueFilename = UUID.randomUUID().toString().substring(0, 10) + "_" + cleanName;
            Path targetPath = targetDir.resolve(uniqueFilename);

            file.transferTo(targetPath.toFile());

            return "/uploads/" + subfolder + "/" + uniqueFilename;
        } catch (IOException e) {
            throw new RuntimeException("Failed to save uploaded file: " + e.getMessage(), e);
        }
    }
}
