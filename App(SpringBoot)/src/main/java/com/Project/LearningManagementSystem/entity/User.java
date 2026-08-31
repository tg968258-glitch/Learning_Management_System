package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "users")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class User {

    @Id
    @Column(name = "uid", length = 10)
    private String uid;

    @Column(name = "username", length = 50, nullable = false, unique = true)
    private String username;

    @Column(name = "email", length = 255, nullable = false, unique = true)
    private String email;

    @Column(name = "recovery_email", length = 255)
    private String recoveryEmail;

    @Column(name = "password_hash", length = 255, nullable = false)
    private String passwordHash;

    @Column(name = "role", length = 20, nullable = false)
    private String role;

    @Column(name = "email_verified", nullable = false)
    private boolean emailVerified = false;

    @Column(name = "recovery_email_verified", nullable = false)
    private boolean recoveryEmailVerified = false;

    @Column(name = "is_active", nullable = false)
    private boolean active = true;

    @Column(name = "deactivated_at")
    private LocalDateTime deactivatedAt;
}
