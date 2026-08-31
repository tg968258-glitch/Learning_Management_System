package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.NotificationDtos.NotificationCreateRequest;
import com.Project.LearningManagementSystem.dto.NotificationDtos.NotificationResponse;
import com.Project.LearningManagementSystem.entity.Notification;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.NotificationRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationRepository notificationRepository;

    public NotificationResponse toResponse(Notification n) {
        return new NotificationResponse(
                n.getNotificationId(),
                n.getUid(),
                n.getSessionId(),
                n.getAssignmentId(),
                n.getNotificationType(),
                n.getTitle(),
                n.getMessage(),
                n.getStatus(),
                n.isRead());
    }

    public List<NotificationResponse> getUserNotifications(String uid) {
        return notificationRepository.findByUidOrderByCreatedAtDesc(uid).stream().map(this::toResponse).toList();
    }

    @Transactional
    public NotificationResponse createNotification(NotificationCreateRequest request) {
        Notification n = new Notification();
        n.setUid(request.getUid());
        n.setSessionId(request.getSession_id());
        n.setAssignmentId(request.getAssignment_id());
        n.setNotificationType(request.getNotification_type());
        n.setTitle(request.getTitle());
        n.setMessage(request.getMessage().trim());
        n.setStatus("sent");
        n.setRead(false);
        n.setCreatedAt(LocalDateTime.now());
        n.setSentAt(LocalDateTime.now());
        notificationRepository.save(n);

        return toResponse(n);
    }

    @Transactional
    public NotificationResponse markAsRead(Integer notificationId) {
        Notification n = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new ResourceNotFoundException("Notification not found: " + notificationId));

        n.setRead(true);
        notificationRepository.save(n);
        return toResponse(n);
    }
}
