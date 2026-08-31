package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.math.BigDecimal;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "student_answers",
    uniqueConstraints = @UniqueConstraint(name = "uq_attempt_question", columnNames = {"attempt_id", "question_id"}))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class StudentAnswer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "answer_id")
    private Integer answerId;

    @Column(name = "attempt_id", nullable = false)
    private Integer attemptId;

    @Column(name = "question_id", nullable = false)
    private Integer questionId;

    @Column(name = "selected_option_id")
    private Integer selectedOptionId;

    @Column(name = "marks_awarded", precision = 6, scale = 2)
    private BigDecimal marksAwarded;
}
