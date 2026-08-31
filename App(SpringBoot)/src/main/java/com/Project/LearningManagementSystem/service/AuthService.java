package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.AuthDtos.LoginRequest;
import com.Project.LearningManagementSystem.dto.AuthDtos.RegisterRequest;
import com.Project.LearningManagementSystem.entity.OtpVerification;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.entity.UserSession;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.UnauthorizedException;
import com.Project.LearningManagementSystem.repository.OtpVerificationRepository;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import com.Project.LearningManagementSystem.repository.UserSessionRepository;
import com.Project.LearningManagementSystem.security.JwtUtils;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final StudentRepository studentRepository;
    private final OtpVerificationRepository otpRepository;
    private final UserSessionRepository sessionRepository;
    private final EmailService emailService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    private static final int OTP_EXPIRY_MINUTES = 2;
    private static final int OTP_RESEND_COOLDOWN_SECONDS = 60;

    public static String hashToken(String token) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(token.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public synchronized String generateUid() {
        List<User> users = userRepository.findAll();
        if (users.isEmpty()) {
            return "USR001";
        }
        int maxNum = users.stream()
            .map(User::getUid)
            .filter(uid -> uid != null && uid.startsWith("USR"))
            .mapToInt(uid -> {
                try {
                    return Integer.parseInt(uid.substring(3));
                } catch (NumberFormatException e) {
                    return 0;
                }
            })
            .max()
            .orElse(0);

        return String.format("USR%03d", maxNum + 1);
    }

    @Transactional
    public Map<String, Object> registerUser(RegisterRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        if (userRepository.existsByEmail(email)) {
            throw new BadRequestException("User with this email already exists");
        }

        if (request.getRecovery_email() != null && request.getRecovery_email().trim().equalsIgnoreCase(email)) {
            throw new BadRequestException("Recovery email cannot be the same as primary email");
        }

        String uid = generateUid();

        User user = new User();
        user.setUid(uid);
        user.setUsername(request.getUsername().trim());
        user.setEmail(email);
        user.setRecoveryEmail(request.getRecovery_email());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setRole("student");
        user.setEmailVerified(false);
        user.setRecoveryEmailVerified(false);
        user.setActive(true);
        userRepository.save(user);

        Student student = new Student();
        student.setUid(uid);
        student.setName(request.getName().trim());
        studentRepository.save(student);

        String otp = createOtp(uid, "email_verification");
        emailService.sendOtpEmail(email, otp, "email_verification", user.getUsername());

        Map<String, Object> response = new HashMap<>();
        response.put("uid", user.getUid());
        response.put("username", user.getUsername());
        response.put("email", user.getEmail());
        response.put("role", user.getRole());
        response.put("email_verified", user.isEmailVerified());
        response.put("is_active", user.isActive());
        response.put("message", "Registration successful. A verification OTP has been sent to your email.");
        return response;
    }

    @Transactional
    public Map<String, Object> authenticateUser(LoginRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new UnauthorizedException("Invalid email or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new UnauthorizedException("Invalid email or password");
        }

        if (!user.isActive()) {
            throw new BadRequestException("Your account is deactivated");
        }

        String accessToken = jwtUtils.generateToken(user.getUid(), user.getRole());
        String refreshToken = UUID.randomUUID().toString();
        String sessionId = UUID.randomUUID().toString();

        UserSession session = new UserSession();
        session.setSessionId(sessionId);
        session.setUid(user.getUid());
        session.setRefreshTokenHash(hashToken(refreshToken));
        session.setExpiresAt(LocalDateTime.now().plusDays(request.isRemember_me() ? 30 : 7));
        session.setCreatedAt(LocalDateTime.now());
        session.setLastUsedAt(LocalDateTime.now());
        sessionRepository.save(session);

        Map<String, Object> result = new HashMap<>();
        result.put("uid", user.getUid());
        result.put("username", user.getUsername());
        result.put("email", user.getEmail());
        result.put("role", user.getRole());
        result.put("email_verified", user.isEmailVerified());
        result.put("access_token", accessToken);
        result.put("refresh_token", refreshToken);
        result.put("session_id", sessionId);
        result.put("token_type", "bearer");
        return result;
    }

    @Transactional
    public String createOtp(String uid, String purpose) {
        String otp = String.format("%06d", new Random().nextInt(1_000_000));

        OtpVerification record = new OtpVerification();
        record.setUid(uid);
        record.setOtpHash(passwordEncoder.encode(otp));
        record.setPurpose(purpose);
        record.setExpiresAt(LocalDateTime.now().plusMinutes(OTP_EXPIRY_MINUTES));
        record.setCreatedAt(LocalDateTime.now());
        record.setAttempts(0);
        record.setUsed(false);
        otpRepository.save(record);

        return otp;
    }

    public void verifyUserOtp(String uid, String purpose, String otp) {
        OtpVerification record = otpRepository.findTopByUidAndPurposeOrderByCreatedAtDesc(uid, purpose)
            .orElseThrow(() -> new BadRequestException("OTP not found"));

        if (record.isUsed()) {
            throw new BadRequestException("OTP has already been used");
        }
        if (record.getExpiresAt().isBefore(LocalDateTime.now())) {
            throw new BadRequestException("OTP has expired");
        }
        if (record.getAttempts() >= 5) {
            throw new BadRequestException("Maximum OTP attempts exceeded");
        }

        if (!passwordEncoder.matches(otp, record.getOtpHash())) {
            record.setAttempts(record.getAttempts() + 1);
            otpRepository.save(record);
            throw new BadRequestException("Invalid OTP");
        }

        record.setUsed(true);
        otpRepository.save(record);
    }

    @Transactional
    public void requestEmailVerification(String email) {
        email = email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new BadRequestException("User not found"));

        if (user.isEmailVerified()) {
            throw new BadRequestException("Email is already verified");
        }

        String otp = createOtp(user.getUid(), "email_verification");
        emailService.sendOtpEmail(email, otp, "email_verification", user.getUsername());
    }

    @Transactional
    public void resendOtp(String email, String purpose) {
        email = email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new BadRequestException("User not found"));

        if ("email_verification".equals(purpose) && user.isEmailVerified()) {
            throw new BadRequestException("Email is already verified");
        }

        Optional<OtpVerification> lastOtp = otpRepository.findTopByUidAndPurposeOrderByCreatedAtDesc(user.getUid(), purpose);
        if (lastOtp.isPresent()) {
            long secondsElapsed = java.time.Duration.between(lastOtp.get().getCreatedAt(), LocalDateTime.now()).getSeconds();
            if (secondsElapsed < OTP_RESEND_COOLDOWN_SECONDS) {
                long remaining = OTP_RESEND_COOLDOWN_SECONDS - secondsElapsed;
                throw new BadRequestException("Please wait " + remaining + " seconds before requesting a new OTP.");
            }
        }

        String otp = createOtp(user.getUid(), purpose);
        emailService.sendOtpEmail(email, otp, purpose, user.getUsername());
    }

    @Transactional
    public void verifyEmail(String email, String otp) {
        email = email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new BadRequestException("User not found"));

        if (user.isEmailVerified()) {
            throw new BadRequestException("Email is already verified");
        }

        verifyUserOtp(user.getUid(), "email_verification", otp);
        user.setEmailVerified(true);
        userRepository.save(user);
    }

    @Transactional
    public void requestPasswordReset(String email) {
        email = email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new BadRequestException("User not found"));

        if (!user.isActive()) {
            throw new BadRequestException("User account is deactivated");
        }

        String otp = createOtp(user.getUid(), "password_reset");
        emailService.sendOtpEmail(email, otp, "password_reset", user.getUsername());
    }

    @Transactional
    public void resetPassword(String email, String otp, String newPassword) {
        email = email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new BadRequestException("User not found"));

        verifyUserOtp(user.getUid(), "password_reset", otp);

        if (passwordEncoder.matches(newPassword, user.getPasswordHash())) {
            throw new BadRequestException("New password cannot be the same as old password");
        }

        user.setPasswordHash(passwordEncoder.encode(newPassword));
        userRepository.save(user);
    }

    @Transactional
    public String refreshAccessToken(String refreshToken) {
        String hashedToken = hashToken(refreshToken);
        UserSession session = sessionRepository.findByRefreshTokenHash(hashedToken)
            .orElseThrow(() -> new UnauthorizedException("Invalid session"));

        if (session.isRevoked() || session.getExpiresAt().isBefore(LocalDateTime.now())) {
            throw new UnauthorizedException("Session expired");
        }

        User user = userRepository.findById(session.getUid())
            .orElseThrow(() -> new BadRequestException("User not found"));

        if (!user.isActive()) {
            throw new BadRequestException("User account is deactivated");
        }

        session.setLastUsedAt(LocalDateTime.now());
        sessionRepository.save(session);

        return jwtUtils.generateToken(user.getUid(), user.getRole());
    }

    @Transactional
    public void logoutUser(String sessionId, String uid) {
        Optional<UserSession> sessionOpt = sessionRepository.findBySessionIdAndUid(sessionId, uid);
        sessionOpt.ifPresent(session -> {
            session.setRevoked(true);
            sessionRepository.save(session);
        });
    }
}
