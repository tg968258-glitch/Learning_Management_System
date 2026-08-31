package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class NotificationDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NotificationCreateRequest {
        @NotBlank(message = "UID cannot be empty")
        private String uid;

        private Integer session_id;
        private Integer assignment_id;

        @NotBlank(message = "Notification type cannot be empty")
        private String notification_type;

        private String title;

        @NotBlank(message = "Message cannot be empty")
        private String message;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NotificationResponse {
        private Integer notification_id;
        private String uid;
        private Integer session_id;
        private Integer assignment_id;
        private String notification_type;
        private String title;
        private String message;
        private String status;
        private boolean is_read;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AuditLogResponse {
        private Integer audit_id;
        private String uid;
        private String action;
        private String entity_type;
        private String entity_id;
    }
}
