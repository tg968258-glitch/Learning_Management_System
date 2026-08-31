package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "quiz_attempts",
    uniqueConstraints = @UniqueConstraint(name = "uq_quiz_student_attempt",
        columnNames = {"quiz_id", "student_id", "attempt_number"}))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class QuizAttempt {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "attempt_id")
    private Integer attemptId;

    @Column(name = "quiz_id", nullable = false)
    private Integer quizId;

    @Column(name = "student_id", nullable = false)
    private Integer studentId;

    @Column(name = "attempt_number", nullable = false)
    private Integer attemptNumber;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "submitted_at")
    private LocalDateTime submittedAt;

    @Column(name = "marks", precision = 6, scale = 2)
    private BigDecimal marks;

    @Column(name = "status", length = 20, nullable = false)
    private String status = "Not Attempted";

    @Column(name = "passed")
    private Boolean passed;
}
