package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class LessonDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonCreateRequest {
        @NotNull(message = "Module ID cannot be null")
        private Integer module_id;

        @NotBlank(message = "Lesson title cannot be empty")
        @Size(min = 2, max = 150, message = "Lesson title must be between 2 and 150 characters")
        private String lesson_title;

        private boolean is_published = false;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonUpdateRequest {
        private String lesson_title;
        private Boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonResponse {
        private Integer lesson_id;
        private Integer module_id;
        private String lesson_title;
        private boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonDetailResponse {
        private Integer lesson_id;
        private Integer module_id;
        private String lesson_title;
        private boolean is_published;
        private List<LessonContentResponse> contents = new ArrayList<>();
        private List<ResourceResponse> resources = new ArrayList<>();
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonContentCreateRequest {
        @NotNull(message = "Lesson ID cannot be null")
        private Integer lesson_id;

        @NotBlank(message = "Content type cannot be empty")
        private String content_type;

        @NotBlank(message = "Content cannot be empty")
        private String content;

        private int sequence_number = 1;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonContentUpdateRequest {
        private String content_type;
        private String content;
        private Integer sequence_number;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LessonContentResponse {
        private Integer content_id;
        private Integer lesson_id;
        private String content_type;
        private String content;
        private int sequence_number;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceCreateRequest {
        @NotNull(message = "Lesson ID cannot be null")
        private Integer lesson_id;

        @NotBlank(message = "Resource name cannot be empty")
        @Size(min = 2, max = 150, message = "Resource name must be between 2 and 150 characters")
        private String resource_name;

        private String resource_type;

        @NotBlank(message = "Resource URL cannot be empty")
        private String resource_url;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceUpdateRequest {
        private String resource_name;
        private String resource_type;
        private String resource_url;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ResourceResponse {
        private Integer resource_id;
        private Integer lesson_id;
        private String resource_name;
        private String resource_type;
        private String resource_url;
    }
}
