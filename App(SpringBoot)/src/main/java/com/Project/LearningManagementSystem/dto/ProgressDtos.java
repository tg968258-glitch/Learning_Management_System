package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.time.LocalDate;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class ProgressDtos {

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class LessonProgressUpdateRequest {
        @NotNull(message = "Progress percentage cannot be null")
        private BigDecimal progress_percentage;

        private boolean completed = false;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class LessonProgressResponse {
        private Integer student_id;
        private Integer lesson_id;
        private BigDecimal progress_percentage;
        private boolean completed;
        private LocalDate completed_date;
        private String lesson_title;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class CourseProgressSummaryResponse {
        private Integer course_id;
        private String course_name;
        private int total_lessons;
        private int completed_lessons;
        private BigDecimal overall_progress_percentage;
    }
}
