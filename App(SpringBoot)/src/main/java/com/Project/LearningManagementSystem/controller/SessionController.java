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
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/sessions")
@Tag(name = "Class Sessions")
@RequiredArgsConstructor
public class SessionController {

    private final SessionService sessionService;

    @GetMapping("/")
    public ResponseEntity<List<ClassSessionResponse>> listAllSessions(
        @RequestParam(required = false) Integer course_id
    ) {
        return ResponseEntity.ok(sessionService.getAllSessions(course_id));
    }

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<ClassSessionResponse>> listSessions(@PathVariable Integer course_id) {
        return ResponseEntity.ok(sessionService.getSessionsByCourse(course_id));
    }

    @GetMapping("/{session_id}")
    public ResponseEntity<ClassSessionResponse> getSingleSession(@PathVariable Integer session_id) {
        return ResponseEntity.ok(sessionService.getSessionById(session_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasRole('TEACHER')")
    public ResponseEntity<ClassSessionResponse> createSession(@Valid @RequestBody ClassSessionCreateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.status(HttpStatus.CREATED).body(sessionService.createSession(request, currentUser.getUid()));
    }

    @PutMapping("/{session_id}")
    @PreAuthorize("hasRole('TEACHER')")
    public ResponseEntity<ClassSessionResponse> updateSession(
        @PathVariable Integer session_id,
        @Valid @RequestBody ClassSessionUpdateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        return ResponseEntity.ok(sessionService.updateSession(session_id, request, currentUser.getUid()));
    }

    @DeleteMapping("/{session_id}")
    @PreAuthorize("hasRole('TEACHER')")
    public ResponseEntity<Map<String, String>> deleteSession(@PathVariable Integer session_id,
        @AuthenticationPrincipal UserPrincipal currentUser) {
        sessionService.deleteSession(session_id, currentUser.getUid());
        return ResponseEntity.ok(Map.of("message", "Session deleted successfully"));
    }
}
