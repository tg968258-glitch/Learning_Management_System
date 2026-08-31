package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.NotificationDtos.NotificationCreateRequest;
import com.Project.LearningManagementSystem.dto.NotificationDtos.NotificationResponse;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.NotificationService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/notifications")
@Tag(name = "Notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping("/my-notifications")
    public ResponseEntity<List<NotificationResponse>> getMyNotifications(
        @RequestParam(required = false, defaultValue = "false") boolean unread_only,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        return ResponseEntity.ok(notificationService.getUserNotifications(currentUser.getUid()));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<NotificationResponse> sendNotification(@Valid @RequestBody NotificationCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(notificationService.createNotification(request));
    }

    @PutMapping("/{notification_id}/read")
    public ResponseEntity<NotificationResponse> markRead(@PathVariable Integer notification_id) {
        return ResponseEntity.ok(notificationService.markAsRead(notification_id));
    }

    @PutMapping("/read-all")
    public ResponseEntity<Map<String, String>> markAllRead(@AuthenticationPrincipal UserPrincipal currentUser) {
        List<NotificationResponse> notifs = notificationService.getUserNotifications(currentUser.getUid());
        for (NotificationResponse n : notifs) {
            notificationService.markAsRead(n.getNotification_id());
        }
        return ResponseEntity.ok(Map.of("message", "Marked " + notifs.size() + " notifications as read"));
    }
}
