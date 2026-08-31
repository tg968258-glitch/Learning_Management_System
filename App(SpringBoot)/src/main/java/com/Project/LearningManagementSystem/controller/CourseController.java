package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.CourseDtos.CourseAssignTeachersRequest;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseCreateRequest;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseResponse;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseUpdateRequest;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.CourseService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
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

@RestController
@RequestMapping("/courses")
@Tag(name = "Courses")
@RequiredArgsConstructor
public class CourseController {

    private final CourseService courseService;

    @GetMapping("/")
    public ResponseEntity<List<CourseResponse>> listCourses(
        @RequestParam(required = false) String status,
        @RequestParam(required = false) String category
    ) {
        return ResponseEntity.ok(courseService.getAllCourses());
    }

    @GetMapping("/{course_id}")
    public ResponseEntity<CourseResponse> getCourseById(@PathVariable Integer course_id) {
        return ResponseEntity.ok(courseService.getCourseById(course_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<CourseResponse> addNewCourse(
        @Valid @RequestBody CourseCreateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        CourseResponse created = courseService.createCourse(request, currentUser.getUid());
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{course_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<CourseResponse> updateExistingCourse(
        @PathVariable Integer course_id,
        @Valid @RequestBody CourseUpdateRequest request
    ) {
        return ResponseEntity.ok(courseService.updateCourse(course_id, request));
    }

    @DeleteMapping("/{course_id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, String>> removeCourse(@PathVariable Integer course_id) {
        courseService.deleteCourse(course_id);
        return ResponseEntity.ok(Map.of("message", "Course deleted successfully"));
    }

    @PostMapping("/{course_id}/teachers")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> assignTeachers(
        @PathVariable Integer course_id,
        @Valid @RequestBody CourseAssignTeachersRequest request
    ) {
        CourseResponse updated = courseService.assignTeachers(course_id, request.getTeacher_ids());
        return ResponseEntity.ok(Map.of(
            "message", "Teachers assigned successfully",
            "course_id", course_id,
            "teachers", updated.getTeachers()
        ));
    }

    @PutMapping("/{course_id}/publish")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<CourseResponse> publishCourse(
        @PathVariable Integer course_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        CourseUpdateRequest req = new CourseUpdateRequest();
        req.setStatus("active");
        return ResponseEntity.ok(courseService.updateCourse(course_id, req));
    }
}
