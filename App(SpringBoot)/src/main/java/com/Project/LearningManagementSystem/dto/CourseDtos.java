package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class CourseDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseCreateRequest {
        @NotBlank(message = "Course name cannot be empty")
        @Size(min = 2, max = 100, message = "Course name must be between 2 and 100 characters")
        private String course_name;

        private String description;
        private String duration;
        private String status = "draft";
        private String category;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseUpdateRequest {
        private String course_name;
        private String description;
        private String duration;
        private String status;
        private String category;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseAssignTeachersRequest {
        private List<Integer> teacher_ids;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseTeacherInfo {
        private Integer teacher_id;
        private String name;
        private String specialization;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseResponse {
        private Integer course_id;
        private String course_name;
        private String description;
        private String duration;
        private String status;
        private String category;
        private List<CourseTeacherInfo> teachers = new ArrayList<>();
    }
}
