package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.ArrayList;
import java.math.BigDecimal;
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
    public static class CourseLessonInfo {
        private Integer lesson_id;
        private Integer module_id;
        private String lesson_title;
        private boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseModuleInfo {
        private Integer module_id;
        private Integer course_id;
        private String module_name;
        private String description;
        private boolean is_published;
        private List<CourseLessonInfo> lessons = new ArrayList<>();
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
        private List<CourseModuleInfo> modules = new ArrayList<>();
        private int module_count;
        private int lesson_count;
        private long enrollment_count;
        private boolean is_enrolled;
        private Integer completed_lessons;
        private BigDecimal overall_progress_percentage;
    }
}
