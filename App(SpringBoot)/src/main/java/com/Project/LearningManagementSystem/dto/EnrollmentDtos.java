package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class EnrollmentDtos {

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class EnrollmentCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;
        private Integer student_id;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class EnrollmentStatusUpdateRequest {
        @NotNull(message = "Status cannot be null")
        private String status;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class EnrollmentResponse {
        private Integer enrollment_id;
        private Integer student_id;
        private Integer course_id;
        private LocalDate enrollment_date;
        private String status;
        private String student_name;
        private String course_name;
    }
}
