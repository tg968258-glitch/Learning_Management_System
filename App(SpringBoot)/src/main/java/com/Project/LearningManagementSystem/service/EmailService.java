package com.Project.LearningManagementSystem.service;

import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${spring.mail.username:}")
    private String fromEmail;

    @Value("${app.email.from-name:LMS Platform}")
    private String fromName;

    private boolean sendHtmlEmail(String toEmail, String subject, String htmlContent) {
        try {
            if (fromEmail == null || fromEmail.isBlank()) {
                log.warn("SMTP email username is not configured. Simulating email send to: {}", toEmail);
                return true;
            }
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            helper.setFrom(fromEmail, fromName);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true);

            mailSender.send(message);
            log.info("Email sent successfully to {} | Subject: {}", toEmail, subject);
            return true;
        } catch (Exception e) {
            log.error("Failed to send email to {}: {}", toEmail, e.getMessage());
            return false;
        }
    }

    public boolean sendOtpEmail(String toEmail, String otp, String purpose, String username) {
        String label = switch (purpose) {
            case "email_verification" -> "Email Verification";
            case "password_reset" -> "Password Reset";
            case "recovery_email_verification" -> "Recovery Email Verification";
            default -> "Verification";
        };

        String greeting = (username != null && !username.isBlank()) ? "Hi " + username + "," : "Hello,";
        String subject = "Your " + label + " OTP - LMS Platform";

        String html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
                .container { max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .otp-box { font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #4F46E5; text-align: center; padding: 20px; background: #EEF2FF; border-radius: 8px; margin: 24px 0; }
                .footer { font-size: 12px; color: #888888; margin-top: 24px; }
            </style>
            </head>
            <body>
                <div class="container">
                    <h2 style="color: #1e1e2e;">%s OTP</h2>
                    <p>%s</p>
                    <p>Use the following OTP to complete your <strong>%s</strong>. This OTP is valid for <strong>2 minutes</strong>.</p>
                    <div class="otp-box">%s</div>
                    <p>If you did not request this OTP, please ignore this email.</p>
                    <div class="footer"><p>&copy; LMS Platform. All rights reserved.</p></div>
                </div>
            </body>
            </html>
            """.formatted(label, greeting, label, otp);

        return sendHtmlEmail(toEmail, subject, html);
    }

    public boolean sendTeacherInvitationEmail(String toEmail, String inviteUrl) {
        String subject = "You're Invited to Join as an Instructor - LMS Platform";
        String html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }
                .container { max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .btn { display: inline-block; padding: 12px 24px; background: #4F46E5; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }
                .footer { font-size: 12px; color: #888888; margin-top: 24px; }
            </style>
            </head>
            <body>
                <div class="container">
                    <h2 style="color: #1e1e2e;">Teacher Invitation</h2>
                    <p>Hello,</p>
                    <p>You have been invited to join our Learning Management System as a teacher/instructor.</p>
                    <p>Click the button below to complete your registration and set up your profile:</p>
                    <a href="%s" class="btn" style="color:white;">Accept Invitation</a>
                    <p>Or paste this link in your browser: <br><a href="%s">%s</a></p>
                    <p>This invitation link expires in 7 days.</p>
                    <div class="footer"><p>&copy; LMS Platform. All rights reserved.</p></div>
                </div>
            </body>
            </html>
            """.formatted(inviteUrl, inviteUrl, inviteUrl);

        return sendHtmlEmail(toEmail, subject, html);
    }
}
