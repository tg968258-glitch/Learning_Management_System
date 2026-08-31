package com.Project.LearningManagementSystem.dto;

import java.time.LocalDate;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class TeacherDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TeacherUpdateRequest {
        private String name;
        private String phone_number;
        private String specialization;
        private String qualification;
        private Integer experience;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TeacherResponse {
        private Integer teacher_id;
        private String uid;
        private String employee_code;
        private String name;
        private String email;
        private String phone_number;
        private String department;
        private String specialization;
        private String qualification;
        private Integer experience;
        private LocalDate joining_date;
    }
}
