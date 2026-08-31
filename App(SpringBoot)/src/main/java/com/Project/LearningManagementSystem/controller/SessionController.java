package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionUpdateRequest;
import com.Project.LearningManagementSystem.service.SessionService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/sessions")
@Tag(name = "Class Sessions")
@RequiredArgsConstructor
public class SessionController {

    private final SessionService sessionService;

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<ClassSessionResponse>> listSessions(@PathVariable Integer course_id) {
        return ResponseEntity.ok(sessionService.getSessionsByCourse(course_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ClassSessionResponse> createSession(@Valid @RequestBody ClassSessionCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(sessionService.createSession(request));
    }

    @PutMapping("/{session_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ClassSessionResponse> updateSession(
        @PathVariable Integer session_id,
        @Valid @RequestBody ClassSessionUpdateRequest request
    ) {
        return ResponseEntity.ok(sessionService.updateSession(session_id, request));
    }

    @DeleteMapping("/{session_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> deleteSession(@PathVariable Integer session_id) {
        sessionService.deleteSession(session_id);
        return ResponseEntity.ok(Map.of("message", "Session deleted successfully"));
    }
}
