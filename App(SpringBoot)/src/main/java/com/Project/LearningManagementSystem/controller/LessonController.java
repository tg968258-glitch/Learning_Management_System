package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.LessonDtos.LessonContentCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonContentResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonDetailResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonUpdateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.ResourceCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.ResourceResponse;
import com.Project.LearningManagementSystem.service.LessonService;
import com.Project.LearningManagementSystem.util.FileUploadUtil;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/lessons")
@Tag(name = "Lessons")
@RequiredArgsConstructor
public class LessonController {

    private final LessonService lessonService;
    private final FileUploadUtil fileUploadUtil;

    @GetMapping("/module/{module_id}")
    public ResponseEntity<List<LessonResponse>> listModuleLessons(@PathVariable Integer module_id) {
        return ResponseEntity.ok(lessonService.getLessonsByModule(module_id));
    }

    @GetMapping("/{lesson_id}")
    public ResponseEntity<LessonDetailResponse> getLessonDetail(@PathVariable Integer lesson_id) {
        return ResponseEntity.ok(lessonService.getLessonDetail(lesson_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<LessonResponse> addLesson(@Valid @RequestBody LessonCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(lessonService.createLesson(request));
    }

    @PutMapping("/{lesson_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<LessonResponse> updateLesson(
        @PathVariable Integer lesson_id,
        @Valid @RequestBody LessonUpdateRequest request
    ) {
        return ResponseEntity.ok(lessonService.updateLesson(lesson_id, request));
    }

    @DeleteMapping("/{lesson_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> removeLesson(@PathVariable Integer lesson_id) {
        lessonService.deleteLesson(lesson_id);
        return ResponseEntity.ok(Map.of("message", "Lesson deleted successfully"));
    }

    @PostMapping("/contents/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<LessonContentResponse> addContent(@Valid @RequestBody LessonContentCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(lessonService.addLessonContent(request));
    }

    @PostMapping("/resources/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ResourceResponse> addResource(@Valid @RequestBody ResourceCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(lessonService.addResource(request));
    }

    @PostMapping(value = "/{lesson_id}/resources/upload-pdf", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ResourceResponse> uploadPdfResource(
        @PathVariable Integer lesson_id,
        @RequestParam("resource_name") String resourceName,
        @RequestParam(value = "resource_type", defaultValue = "pdf") String resourceType,
        @RequestParam("file") MultipartFile file
    ) {
        String fileUrl = fileUploadUtil.saveUploadedFile(file, "resources");
        ResourceCreateRequest req = new ResourceCreateRequest(lesson_id, resourceName, resourceType, fileUrl);
        return ResponseEntity.status(HttpStatus.CREATED).body(lessonService.addResource(req));
    }
}
