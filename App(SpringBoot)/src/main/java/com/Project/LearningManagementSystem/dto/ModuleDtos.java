package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class ModuleDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ModuleCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;

        @NotBlank(message = "Module name cannot be empty")
        @Size(min = 2, max = 150, message = "Module name must be between 2 and 150 characters")
        private String module_name;

        private String description;
        private boolean is_published = false;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ModuleUpdateRequest {
        private String module_name;
        private String description;
        private Boolean is_published;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ModuleResponse {
        private Integer module_id;
        private Integer course_id;
        private String module_name;
        private String description;
        private boolean is_published;
        private String published_by;
    }
}
