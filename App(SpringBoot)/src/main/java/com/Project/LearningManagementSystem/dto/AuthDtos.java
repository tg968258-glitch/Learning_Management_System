package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class AuthDtos {

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class RegisterRequest {
        @NotBlank(message = "Username cannot be empty")
        @Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
        private String username;

        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "Name cannot be empty")
        @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
        private String name;

        private String recovery_email;

        @NotBlank(message = "Password cannot be empty")
        @Size(min = 8, max = 100, message = "Password must be between 8 and 100 characters")
        private String password;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class LoginRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "Password cannot be empty")
        private String password;

        private boolean remember_me = false;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class RefreshTokenRequest {
        @NotBlank(message = "Refresh token cannot be empty")
        private String refresh_token;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class LogoutRequest {
        @NotBlank(message = "Session ID cannot be empty")
        private String session_id;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class SendVerificationOTPRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class VerifyEmailOTPRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "OTP cannot be empty")
        @Pattern(regexp = "^\\d{6}$", message = "OTP must be exactly 6 digits")
        private String otp;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class ResendOTPRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "Purpose cannot be empty")
        private String purpose;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class ForgotPasswordRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class ResetPasswordRequest {
        @NotBlank(message = "Email cannot be empty")
        @Email(message = "Invalid email format")
        private String email;

        @NotBlank(message = "OTP cannot be empty")
        @Pattern(regexp = "^\\d{6}$", message = "OTP must be exactly 6 digits")
        private String otp;

        @NotBlank(message = "Password cannot be empty")
        @Size(min = 8, max = 100, message = "Password must be between 8 and 100 characters")
        private String new_password;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class AcceptTeacherInviteRequest {
        @NotBlank(message = "Invitation token cannot be empty")
        private String token;

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

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class UserProfileResponse {
        private String uid;
        private String username;
        private String email;
        private String role;
        private boolean email_verified;
        private boolean is_active;
    }
}
