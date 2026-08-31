package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDate;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "lesson_progress")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class LessonProgress {

    @EmbeddedId
    private LessonProgressId id;

    @Column(name = "progress_percentage", nullable = false, precision = 5, scale = 2)
    private BigDecimal progressPercentage = BigDecimal.ZERO;

    @Column(name = "completed", nullable = false)
    private boolean completed = false;

    @Column(name = "completed_date")
    private LocalDate completedDate;
}
