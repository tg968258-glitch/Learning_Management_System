package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
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
    public static class CreateTeacherRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "Username cannot be empty")
        @Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
        private String username;

        @NotBlank(message = "Password cannot be empty")
        @Size(min = 8, max = 100, message = "Password must be between 8 and 100 characters")
        private String password;

        @NotBlank(message = "Name cannot be empty")
        @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
        private String name;

        private String phone_number;
        private String specialization;
        private String qualification;
        private Integer experience;
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
