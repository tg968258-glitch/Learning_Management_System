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
@Table(name = "submissions",
    uniqueConstraints = @UniqueConstraint(name = "uq_assignment_student", columnNames = {"assignment_id", "student_id"}))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class Submission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "submission_id")
    private Integer submissionId;

    @Column(name = "assignment_id", nullable = false)
    private Integer assignmentId;

    @Column(name = "student_id", nullable = false)
    private Integer studentId;

    @Column(name = "submission_date")
    private LocalDateTime submissionDate;

    @Column(name = "submission_text", columnDefinition = "TEXT")
    private String submissionText;

    @Column(name = "submission_file", length = 500)
    private String submissionFile;

    @Column(name = "status", length = 30, nullable = false)
    private String status = "submitted";

    @Column(name = "marks", precision = 6, scale = 2)
    private BigDecimal marks;

    @Column(name = "graded_by")
    private Integer gradedBy;

    @Column(name = "feedback", columnDefinition = "TEXT")
    private String feedback;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
