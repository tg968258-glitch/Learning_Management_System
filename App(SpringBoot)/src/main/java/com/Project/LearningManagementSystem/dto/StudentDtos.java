package com.Project.LearningManagementSystem.dto;

import java.time.LocalDate;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class StudentDtos {

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class StudentUpdateRequest {
        private String name;
        private LocalDate date_of_birth;
        private String gender;
        private String phone_number;
    }

    @Getter @Setter @NoArgsConstructor @AllArgsConstructor
    public static class StudentResponse {
        private Integer student_id;
        private String uid;
        private String roll_number;
        private String name;
        private String email;
        private LocalDate date_of_birth;
        private String gender;
        private String phone_number;
        private LocalDate enrollment_date;
    }
}
