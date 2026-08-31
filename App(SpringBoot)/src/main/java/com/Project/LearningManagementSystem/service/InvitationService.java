package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.entity.TeacherInvitation;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.repository.TeacherInvitationRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class InvitationService {

    private final TeacherInvitationRepository invitationRepository;
    private final UserRepository userRepository;
    private final TeacherRepository teacherRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;
    private final AuthService authService;

    private static final int INVITE_EXPIRY_HOURS = 48;

    @Transactional
    public Map<String, Object> createTeacherInvitation(String email, String invitedByUid, String acceptUrlBase) {
        email = email.trim().toLowerCase();

        if (userRepository.existsByEmail(email)) {
            throw new BadRequestException("A user with this email already exists.");
        }

        invitationRepository.findByEmailAndUsed(email, false).ifPresent(existing -> {
            if (existing.getExpiresAt().isAfter(LocalDateTime.now())) {
                throw new BadRequestException("An active invitation already exists for this email.");
            }
        });

        String token = UUID.randomUUID().toString();
        String tokenHash = AuthService.hashToken(token);

        TeacherInvitation invitation = new TeacherInvitation();
        invitation.setEmail(email);
        invitation.setTokenHash(tokenHash);
        invitation.setInvitedBy(invitedByUid);
        invitation.setUsed(false);
        invitation.setExpiresAt(LocalDateTime.now().plusHours(INVITE_EXPIRY_HOURS));
        invitation.setCreatedAt(LocalDateTime.now());
        invitationRepository.save(invitation);

        String baseUrl = (acceptUrlBase != null && !acceptUrlBase.isBlank()) ? acceptUrlBase : "http://localhost:3000/accept-invite";
        String inviteUrl = baseUrl + "?token=" + token;

        emailService.sendTeacherInvitationEmail(email, inviteUrl);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Invitation sent to " + email);
        response.put("invitation_id", invitation.getInvitationId());
        response.put("email", email);
        response.put("expires_in_hours", INVITE_EXPIRY_HOURS);
        return response;
    }

    @Transactional
    public Map<String, Object> acceptTeacherInvitation(String token, String username, String password,
                                                      String name, String phoneNumber, String specialization,
                                                      String qualification, Integer experience) {
        String tokenHash = AuthService.hashToken(token);
        TeacherInvitation invitation = invitationRepository.findByTokenHash(tokenHash)
            .orElseThrow(() -> new BadRequestException("Invalid or already used invitation token."));

        if (invitation.isUsed()) {
            throw new BadRequestException("Invitation has already been used");
        }

        if (invitation.getExpiresAt().isBefore(LocalDateTime.now())) {
            throw new BadRequestException("This invitation has expired. Please ask an admin to send a new one.");
        }

        if (userRepository.existsByEmail(invitation.getEmail())) {
            throw new BadRequestException("A user with this email already exists.");
        }

        String uid = authService.generateUid();

        User user = new User();
        user.setUid(uid);
        user.setUsername(username.trim());
        user.setEmail(invitation.getEmail());
        user.setPasswordHash(passwordEncoder.encode(password));
        user.setRole("teacher");
        user.setEmailVerified(true);
        user.setActive(true);
        userRepository.save(user);

        Teacher teacher = new Teacher();
        teacher.setUid(uid);
        teacher.setName(name.trim());
        teacher.setPhoneNumber(phoneNumber);
        teacher.setSpecialization(specialization);
        teacher.setQualification(qualification);
        teacher.setExperience(experience);
        teacherRepository.save(teacher);

        invitation.setUsed(true);
        invitationRepository.save(invitation);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Invitation accepted. Your teacher account has been created.");
        response.put("uid", user.getUid());
        response.put("username", user.getUsername());
        response.put("email", user.getEmail());
        response.put("role", user.getRole());
        response.put("email_verified", user.isEmailVerified());
        response.put("teacher_id", teacher.getTeacherId());
        return response;
    }
}
