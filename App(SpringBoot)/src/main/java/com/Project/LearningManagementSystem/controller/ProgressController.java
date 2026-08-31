package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.ProgressDtos.CourseProgressSummaryResponse;
import com.Project.LearningManagementSystem.dto.ProgressDtos.LessonProgressResponse;
import com.Project.LearningManagementSystem.dto.ProgressDtos.LessonProgressUpdateRequest;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.ProgressService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/progress")
@Tag(name = "Lesson Progress")
@PreAuthorize("hasRole('STUDENT')")
@RequiredArgsConstructor
public class ProgressController {

    private final ProgressService progressService;
    private final StudentRepository studentRepository;

    @GetMapping("/lesson/{lesson_id}")
    public ResponseEntity<LessonProgressResponse> getMyLessonProgress(
        @PathVariable Integer lesson_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(progressService.getStudentProgress(student.getStudentId()).stream()
            .filter(p -> p.getLesson_id().equals(lesson_id))
            .findFirst()
            .orElse(new LessonProgressResponse(student.getStudentId(), lesson_id, java.math.BigDecimal.ZERO, false, null, null)));
    }

    @PutMapping("/lesson/{lesson_id}")
    public ResponseEntity<LessonProgressResponse> recordLessonProgress(
        @PathVariable Integer lesson_id,
        @Valid @RequestBody LessonProgressUpdateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(progressService.updateLessonProgress(student.getStudentId(), lesson_id, request));
    }

    @GetMapping("/course/{course_id}")
    public ResponseEntity<CourseProgressSummaryResponse> getMyCourseProgress(
        @PathVariable Integer course_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(progressService.getCourseProgressSummary(student.getStudentId(), course_id));
    }
}
