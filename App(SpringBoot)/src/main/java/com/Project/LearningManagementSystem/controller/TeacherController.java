package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.TeacherDtos.TeacherResponse;
import com.Project.LearningManagementSystem.dto.TeacherDtos.TeacherUpdateRequest;
import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.exception.ForbiddenException;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.TeacherService;
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
@RequestMapping("/teachers")
@Tag(name = "Teachers")
@RequiredArgsConstructor
public class TeacherController {

    private final TeacherService teacherService;
    private final TeacherRepository teacherRepository;

    @GetMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<List<Teacher>> getTeachers() {
        return ResponseEntity.ok(teacherService.getAllTeachers());
    }

    @GetMapping("/{teacher_id}")
    public ResponseEntity<TeacherResponse> getTeacherById(
        @PathVariable Integer teacher_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Teacher teacher = teacherRepository.findById(teacher_id)
            .orElseThrow(() -> new RuntimeException("Teacher not found"));

        if ("TEACHER".equalsIgnoreCase(currentUser.getRole()) && !teacher.getUid().equals(currentUser.getUid())) {
            throw new ForbiddenException("You can only view your own teacher profile");
        }

        return ResponseEntity.ok(teacherService.getTeacherProfile(teacher.getUid()));
    }

    @PutMapping("/{teacher_id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> editTeacher(
        @PathVariable Integer teacher_id,
        @Valid @RequestBody TeacherUpdateRequest request
    ) {
        Teacher teacher = teacherRepository.findById(teacher_id)
            .orElseThrow(() -> new RuntimeException("Teacher not found"));
        TeacherResponse updated = teacherService.updateTeacherProfile(teacher.getUid(), request);
        return ResponseEntity.ok(Map.of("message", "Teacher updated successfully", "teacher", updated));
    }

    @DeleteMapping("/{teacher_id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, String>> removeTeacher(@PathVariable Integer teacher_id) {
        teacherRepository.deleteById(teacher_id);
        return ResponseEntity.ok(Map.of("message", "Teacher deleted successfully"));
    }
}
