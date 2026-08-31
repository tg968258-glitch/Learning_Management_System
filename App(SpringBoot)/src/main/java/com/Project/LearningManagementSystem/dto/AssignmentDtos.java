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

public class AssignmentDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AssignmentCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;

        @NotNull(message = "Module ID cannot be null")
        private Integer module_id;

        @NotBlank(message = "Title cannot be empty")
        @Size(min = 2, max = 150, message = "Title must be between 2 and 150 characters")
        private String title;

        private String description;

        @NotNull(message = "Due date cannot be null")
        private LocalDateTime due_date;

        @NotNull(message = "Max marks cannot be null")
        private BigDecimal max_marks;

        @NotNull(message = "Passing marks cannot be null")
        private BigDecimal passing_marks;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AssignmentUpdateRequest {
        private String title;
        private String description;
        private LocalDateTime due_date;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SubmissionCreateRequest {
        private String submission_text;
        private String submission_file;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SubmissionGradeRequest {
        @NotNull(message = "Marks cannot be null")
        private BigDecimal marks;

        private String feedback;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SubmissionResponse {
        private Integer submission_id;
        private Integer assignment_id;
        private Integer student_id;
        private LocalDateTime submission_date;
        private String submission_text;
        private String submission_file;
        private String status;
        private BigDecimal marks;
        private Integer graded_by;
        private String feedback;
        private String student_name;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AssignmentResponse {
        private Integer assignment_id;
        private Integer course_id;
        private Integer module_id;
        private String title;
        private String description;
        private LocalDateTime due_date;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AssignmentDetailResponse {
        private Integer assignment_id;
        private Integer course_id;
        private Integer module_id;
        private String title;
        private String description;
        private LocalDateTime due_date;
        private BigDecimal max_marks;
        private BigDecimal passing_marks;
        private List<SubmissionResponse> submissions = new ArrayList<>();
    }
}
