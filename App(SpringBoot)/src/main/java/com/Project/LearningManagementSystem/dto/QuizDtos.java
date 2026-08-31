package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class QuizDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OptionCreateRequest {
        @NotBlank(message = "Option text cannot be empty")
        private String option_text;
        private boolean is_correct = false;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OptionResponse {
        private Integer option_id;
        private Integer question_id;
        private String option_text;
        private Boolean is_correct; // May be null when student views quiz
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuestionCreateRequest {
        @NotBlank(message = "Question text cannot be empty")
        private String question_text;
        private String question_type = "mcq";
        private BigDecimal marks = BigDecimal.ONE;
        private List<OptionCreateRequest> options = new ArrayList<>();
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuestionResponse {
        private Integer question_id;
        private Integer quiz_id;
        private String question_text;
        private String question_type;
        private BigDecimal marks;
        private List<OptionResponse> options = new ArrayList<>();
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizCreateRequest {
        @NotNull(message = "Lesson ID cannot be null")
        private Integer lesson_id;

        @NotBlank(message = "Title cannot be empty")
        @Size(min = 2, max = 150, message = "Title must be between 2 and 150 characters")
        private String title;

        private String description;

        @NotNull(message = "Max marks cannot be null")
        private BigDecimal max_marks;

        @NotNull(message = "Passing marks cannot be null")
        private BigDecimal passing_marks;

        private Integer duration_minutes;
        private int max_attempts = 1;
        private boolean is_published = false;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizUpdateRequest {
        private String title;
        private String description;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
        private Integer duration_minutes;
        private Integer max_attempts;
        private Boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizResponse {
        private Integer quiz_id;
        private Integer lesson_id;
        private String title;
        private String description;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
        private Integer duration_minutes;
        private int max_attempts;
        private boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizDetailResponse {
        private Integer quiz_id;
        private Integer lesson_id;
        private String title;
        private String description;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
        private Integer duration_minutes;
        private int max_attempts;
        private boolean is_published;
        private List<QuestionResponse> questions = new ArrayList<>();
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SubmitAnswerItem {
        @NotNull(message = "Question ID cannot be null")
        private Integer question_id;
        private Integer selected_option_id;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizSubmitRequest {
        private List<SubmitAnswerItem> answers = new ArrayList<>();
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StudentAnswerResponse {
        private Integer answer_id;
        private Integer attempt_id;
        private Integer question_id;
        private Integer selected_option_id;
        private BigDecimal marks_awarded;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuizAttemptResponse {
        private Integer attempt_id;
        private Integer quiz_id;
        private Integer student_id;
        private int attempt_number;
        private LocalDateTime started_at;
        private LocalDateTime submitted_at;
        private BigDecimal marks;
        private String status;
        private Boolean passed;
        private List<StudentAnswerResponse> answers = new ArrayList<>();
    }
}
