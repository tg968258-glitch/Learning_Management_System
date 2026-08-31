package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.AuthDtos.AcceptTeacherInviteRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.ForgotPasswordRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.LoginRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.LogoutRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.RefreshTokenRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.RegisterRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.ResendOTPRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.ResetPasswordRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.SendVerificationOTPRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.UserProfileResponse;
import com.Project.LearningManagementSystem.dto.AuthDtos.VerifyEmailOTPRequest;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.AuthService;
import com.Project.LearningManagementSystem.service.InvitationService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
@Tag(name = "Authentication")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final InvitationService invitationService;

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(authService.registerUser(request));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@Valid @RequestBody LoginRequest request) {
        Map<String, Object> result = authService.authenticateUser(request);
        return ResponseEntity.ok(Map.of("message", "Login successful", "data", result));
    }

    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout(
        @Valid @RequestBody LogoutRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        authService.logoutUser(request.getSession_id(), currentUser.getUid());
        return ResponseEntity.ok(Map.of("message", "Logout successful"));
    }

    @GetMapping("/me")
    public ResponseEntity<UserProfileResponse> getMyProfile(@AuthenticationPrincipal UserPrincipal currentUser) {
        UserProfileResponse resp = new UserProfileResponse(
            currentUser.getUid(),
            currentUser.getUsername(),
            currentUser.getEmail(),
            currentUser.getRole(),
            true,
            currentUser.isEnabled()
        );
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/send-verification-otp")
    public ResponseEntity<Map<String, String>> sendVerificationOtp(@Valid @RequestBody SendVerificationOTPRequest request) {
        authService.requestEmailVerification(request.getEmail());
        return ResponseEntity.ok(Map.of("message", "Verification OTP sent to your email. It expires in 2 minutes."));
    }

    @PostMapping("/verify-email")
    public ResponseEntity<Map<String, String>> verifyEmail(@Valid @RequestBody VerifyEmailOTPRequest request) {
        authService.verifyEmail(request.getEmail(), request.getOtp());
        return ResponseEntity.ok(Map.of("message", "Email verified successfully"));
    }

    @PostMapping("/resend-otp")
    public ResponseEntity<Map<String, String>> resendOtp(@Valid @RequestBody ResendOTPRequest request) {
        authService.resendOtp(request.getEmail(), request.getPurpose());
        return ResponseEntity.ok(Map.of("message", "A new OTP has been sent to your email. It expires in 2 minutes."));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<Map<String, String>> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        authService.requestPasswordReset(request.getEmail());
        return ResponseEntity.ok(Map.of("message", "Password reset OTP sent to your email. It expires in 2 minutes."));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<Map<String, String>> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        authService.resetPassword(request.getEmail(), request.getOtp(), request.getNew_password());
        return ResponseEntity.ok(Map.of("message", "Password reset successfully"));
    }

    @PostMapping("/refresh")
    public ResponseEntity<Map<String, String>> refresh(@Valid @RequestBody RefreshTokenRequest request) {
        String token = authService.refreshAccessToken(request.getRefresh_token());
        return ResponseEntity.ok(Map.of("access_token", token, "token_type", "bearer"));
    }

    @PostMapping("/accept-teacher-invite")
    public ResponseEntity<Map<String, Object>> acceptTeacherInvite(@Valid @RequestBody AcceptTeacherInviteRequest request) {
        Map<String, Object> result = invitationService.acceptTeacherInvitation(
            request.getToken(), request.getUsername(), request.getPassword(),
            request.getName(), request.getPhone_number(), request.getSpecialization(),
            request.getQualification(), request.getExperience()
        );
        return ResponseEntity.ok(result);
    }
}
