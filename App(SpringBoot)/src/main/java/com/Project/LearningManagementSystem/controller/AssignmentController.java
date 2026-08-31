package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentCreateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentDetailResponse;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentResponse;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentUpdateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionCreateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionGradeRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionResponse;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.AssignmentService;
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
import org.springframework.security.core.annotation.AuthenticationPrincipal;
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
@RequestMapping("/assignments")
@Tag(name = "Assignments")
@RequiredArgsConstructor
public class AssignmentController {

    private final AssignmentService assignmentService;
    private final StudentRepository studentRepository;
    private final TeacherRepository teacherRepository;
    private final FileUploadUtil fileUploadUtil;

    @GetMapping("/")
    public ResponseEntity<List<AssignmentResponse>> listAssignments(
            @RequestParam(required = false) Integer course_id,
            @RequestParam(required = false) Integer module_id) {

        if (course_id != null) {
            return ResponseEntity.ok(
                    assignmentService.getAssignmentsByCourse(course_id));
        }

        return ResponseEntity.ok(List.of());
    }

    @GetMapping("/{assignment_id}")
    public ResponseEntity<AssignmentDetailResponse> getAssignment(
            @PathVariable Integer assignment_id) {
        return ResponseEntity.ok(
                assignmentService.getAssignmentDetail(assignment_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<AssignmentResponse> createAssignment(
            @Valid @RequestBody AssignmentCreateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(
                        assignmentService.createAssignment(
                                request,
                                currentUser.getUid()));
    }

    @PutMapping("/{assignment_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<AssignmentResponse> updateAssignment(
            @PathVariable Integer assignment_id,
            @Valid @RequestBody AssignmentUpdateRequest request) {

        return ResponseEntity.ok(
                assignmentService.updateAssignment(
                        assignment_id,
                        request));
    }

    @DeleteMapping("/{assignment_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> removeAssignment(
            @PathVariable Integer assignment_id) {

        assignmentService.deleteAssignment(assignment_id);

        return ResponseEntity.ok(
                Map.of("message", "Assignment deleted successfully"));
    }

    @PostMapping("/{assignment_id}/submit")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<SubmissionResponse> submitAssignment(
            @PathVariable Integer assignment_id,
            @Valid @RequestBody SubmissionCreateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        Student student = studentRepository
                .findByUid(currentUser.getUid())
                .orElseThrow(
                        () -> new ResourceNotFoundException(
                                "Student profile not found"));

        return ResponseEntity.ok(
                assignmentService.submitAssignment(
                        assignment_id,
                        student.getStudentId(),
                        request));
    }

    @PostMapping(value = "/{assignment_id}/submit-file", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<SubmissionResponse> submitAssignmentWithFile(
            @PathVariable Integer assignment_id,
            @RequestParam(value = "submission_text", required = false) String submissionText,
            @RequestParam(value = "file", required = false) MultipartFile file,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        Student student = studentRepository
                .findByUid(currentUser.getUid())
                .orElseThrow(
                        () -> new ResourceNotFoundException(
                                "Student profile not found"));

        String fileUrl = null;

        if (file != null && !file.isEmpty()) {
            fileUrl = fileUploadUtil.saveUploadedFile(
                    file,
                    "assignments");
        }

        SubmissionCreateRequest request = new SubmissionCreateRequest(
                submissionText,
                fileUrl);

        return ResponseEntity.ok(
                assignmentService.submitAssignment(
                        assignment_id,
                        student.getStudentId(),
                        request));
    }

    @PutMapping("/{assignment_id}/submissions/{student_id}/grade")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<SubmissionResponse> gradeSubmission(
            @PathVariable Integer assignment_id,
            @PathVariable Integer student_id,
            @Valid @RequestBody SubmissionGradeRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {

        Integer teacherId = null;

        if ("TEACHER".equalsIgnoreCase(currentUser.getRole())) {

            Teacher teacher = teacherRepository
                    .findByUid(currentUser.getUid())
                    .orElseThrow(
                            () -> new ResourceNotFoundException(
                                    "Teacher profile not found"));

            teacherId = teacher.getTeacherId();
        }

        return ResponseEntity.ok(
                assignmentService.gradeSubmission(
                        assignment_id,
                        student_id,
                        teacherId,
                        request));
    }
}