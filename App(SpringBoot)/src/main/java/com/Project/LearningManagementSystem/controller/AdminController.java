package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.AdminDtos.CreateTeacherRequest;
import com.Project.LearningManagementSystem.dto.AdminDtos.InviteTeacherRequest;
import com.Project.LearningManagementSystem.dto.AdminDtos.UserResponse;
import com.Project.LearningManagementSystem.dto.AdminDtos.UserStatusUpdateRequest;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.AdminService;
import com.Project.LearningManagementSystem.service.InvitationService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
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
@RequestMapping("/admin")
@Tag(name = "Admin")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;
    private final InvitationService invitationService;

    @GetMapping("/dashboard")
    public ResponseEntity<Map<String, Object>> adminDashboard() {
        return ResponseEntity.ok(adminService.getDashboardData());
    }

    @GetMapping("/users")
    public ResponseEntity<List<UserResponse>> listUsers(
            @RequestParam(required = false) String role,
            @RequestParam(required = false) Boolean is_active) {
        List<User> users = adminService.getAllUsers(role, is_active);
        List<UserResponse> responses = users.stream().map(u -> new UserResponse(
                u.getUid(), u.getUsername(), u.getEmail(), u.getRole(),
                u.isEmailVerified(), u.isActive())).toList();
        return ResponseEntity.ok(responses);
    }

    @PutMapping("/users/{uid}/status")
    public ResponseEntity<Map<String, Object>> updateUserStatus(
            @PathVariable String uid,
            @Valid @RequestBody UserStatusUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        if (uid.equals(currentUser.getUid()) && !request.is_active()) {
            throw new BadRequestException("Admin cannot deactivate their own account");
        }
        User updated = adminService.toggleUserActiveStatus(uid, request.is_active());
        return ResponseEntity.ok(Map.of(
                "message", "User status successfully updated to " + (request.is_active() ? "active" : "inactive"),
                "uid", updated.getUid(),
                "is_active", updated.isActive()));
    }

    @PostMapping("/create-teacher")
    public ResponseEntity<Map<String, Object>> createTeacher(@Valid @RequestBody CreateTeacherRequest request) {
        return ResponseEntity.ok(adminService.createTeacherDirectly(
                request.getEmail(), request.getUsername(), request.getPassword(),
                request.getName(), request.getPhone_number(), request.getSpecialization(),
                request.getQualification(), request.getExperience()));
    }

    @PostMapping("/invite-teacher")
    public ResponseEntity<Map<String, Object>> inviteTeacher(
            @Valid @RequestBody InviteTeacherRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.ok(invitationService.createTeacherInvitation(
                request.getEmail(), currentUser.getUid(), request.getAccept_url_base()));
    }
}
