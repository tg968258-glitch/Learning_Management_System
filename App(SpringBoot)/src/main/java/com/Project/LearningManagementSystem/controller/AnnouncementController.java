package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementUpdateRequest;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.AnnouncementService;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/announcements")
@Tag(name = "Announcements")
@RequiredArgsConstructor
public class AnnouncementController {

    private final AnnouncementService announcementService;

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<AnnouncementResponse>> listAnnouncements(@PathVariable Integer course_id) {
        return ResponseEntity.ok(announcementService.getAnnouncementsByCourse(course_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<AnnouncementResponse> createAnnouncement(
            @Valid @RequestBody AnnouncementCreateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(announcementService.createAnnouncement(request, currentUser.getUid()));
    }

    @PutMapping("/{announcement_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<AnnouncementResponse> updateAnnouncement(
            @PathVariable Integer announcement_id,
            @Valid @RequestBody AnnouncementUpdateRequest request) {
        return ResponseEntity.ok(announcementService.updateAnnouncement(announcement_id, request));
    }

    @DeleteMapping("/{announcement_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> deleteAnnouncement(@PathVariable Integer announcement_id) {
        announcementService.deleteAnnouncement(announcement_id);
        return ResponseEntity.ok(Map.of("message", "Announcement deleted successfully"));
    }
}
