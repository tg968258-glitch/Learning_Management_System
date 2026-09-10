package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class AdminDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserStatusUpdateRequest {
        private boolean is_active;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class InviteTeacherRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        private String accept_url_base;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserResponse {
        private String uid;
        private String username;
        private String email;
        private String role;
        private boolean email_verified;
        private boolean is_active;
    }
}
