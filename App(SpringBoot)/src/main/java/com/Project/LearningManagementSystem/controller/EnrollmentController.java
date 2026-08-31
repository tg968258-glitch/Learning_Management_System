package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.EnrollmentDtos.EnrollmentCreateRequest;
import com.Project.LearningManagementSystem.dto.EnrollmentDtos.EnrollmentResponse;
import com.Project.LearningManagementSystem.dto.EnrollmentDtos.EnrollmentStatusUpdateRequest;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.EnrollmentService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/enrollments")
@Tag(name = "Enrollments")
@RequiredArgsConstructor
public class EnrollmentController {

    private final EnrollmentService enrollmentService;
    private final StudentRepository studentRepository;

    @GetMapping("/my-enrollments")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<List<EnrollmentResponse>> getMyEnrollments(@AuthenticationPrincipal UserPrincipal currentUser) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(enrollmentService.getStudentEnrollments(student.getStudentId()));
    }

    @GetMapping("/course/{course_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<List<EnrollmentResponse>> getEnrollmentsForCourse(@PathVariable Integer course_id) {
        return ResponseEntity.ok(enrollmentService.getCourseEnrollments(course_id));
    }

    @PostMapping("/")
    public ResponseEntity<EnrollmentResponse> addEnrollment(
        @Valid @RequestBody EnrollmentCreateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Integer targetStudentId;
        if ("STUDENT".equalsIgnoreCase(currentUser.getRole())) {
            Student student = studentRepository.findByUid(currentUser.getUid())
                .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
            targetStudentId = student.getStudentId();
        } else {
            targetStudentId = request.getStudent_id();
        }

        EnrollmentResponse resp = enrollmentService.enrollStudent(targetStudentId, request.getCourse_id());
        return ResponseEntity.status(HttpStatus.CREATED).body(resp);
    }

    @PutMapping("/{enrollment_id}/status")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<EnrollmentResponse> changeEnrollmentStatus(
        @PathVariable Integer enrollment_id,
        @Valid @RequestBody EnrollmentStatusUpdateRequest request
    ) {
        return ResponseEntity.ok(enrollmentService.updateEnrollmentStatus(enrollment_id, request.getStatus()));
    }
}
