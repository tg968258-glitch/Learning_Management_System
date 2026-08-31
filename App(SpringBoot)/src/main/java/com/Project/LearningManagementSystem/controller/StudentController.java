package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.StudentDtos.StudentResponse;
import com.Project.LearningManagementSystem.dto.StudentDtos.StudentUpdateRequest;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.exception.ForbiddenException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.StudentService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/students")
@Tag(name = "Students")
@RequiredArgsConstructor
public class StudentController {

    private final StudentService studentService;
    private final StudentRepository studentRepository;

    @GetMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<List<Student>> getStudents() {
        return ResponseEntity.ok(studentService.getAllStudents());
    }

    @GetMapping("/me")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<Map<String, Object>> getMyProfile(@AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.ok(Map.of("student", studentService.getStudentProfile(currentUser.getUid())));
    }

    @GetMapping("/{student_id}")
    public ResponseEntity<StudentResponse> getSingleStudent(
        @PathVariable Integer student_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findById(student_id)
            .orElseThrow(() -> new RuntimeException("Student not found"));

        if ("STUDENT".equalsIgnoreCase(currentUser.getRole()) && !student.getUid().equals(currentUser.getUid())) {
            throw new ForbiddenException("You can only view your own student profile");
        }

        return ResponseEntity.ok(studentService.getStudentProfile(student.getUid()));
    }

    @PutMapping("/me")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<Map<String, Object>> updateMyProfile(
        @Valid @RequestBody StudentUpdateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        StudentResponse updated = studentService.updateStudentProfile(currentUser.getUid(), request);
        return ResponseEntity.ok(Map.of("message", "Profile updated successfully", "student", updated));
    }

    @PutMapping("/{student_id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> updateExistingStudent(
        @PathVariable Integer student_id,
        @Valid @RequestBody StudentUpdateRequest request
    ) {
        Student student = studentRepository.findById(student_id)
            .orElseThrow(() -> new RuntimeException("Student not found"));
        StudentResponse updated = studentService.updateStudentProfile(student.getUid(), request);
        return ResponseEntity.ok(Map.of("message", "Student updated successfully", "student", updated));
    }

    @DeleteMapping("/{student_id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, String>> deleteExistingStudent(@PathVariable Integer student_id) {
        studentRepository.deleteById(student_id);
        return ResponseEntity.ok(Map.of("message", "Student deleted successfully"));
    }
}
