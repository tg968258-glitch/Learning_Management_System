package com.Project.LearningManagementSystem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.time.LocalTime;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

public class CommunicationDtos {

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ClassSessionCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;

        private Integer teacher_id;

        @NotNull(message = "Session date cannot be null")
        private LocalDate session_date;

        private LocalTime start_time;
        private LocalTime end_time;

        @Size(max = 200, message = "Topic must be between 2 and 200 characters")
        private String topic;

        @Size(max = 500, message = "Meeting link must not exceed 500 characters")
        private String meeting_link;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ClassSessionUpdateRequest {
        private Integer teacher_id;
        private LocalDate session_date;
        private LocalTime start_time;
        private LocalTime end_time;
        private String topic;

        @Size(max = 500, message = "Meeting link must not exceed 500 characters")
        private String meeting_link;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ClassSessionResponse {
        private Integer session_id;
        private Integer course_id;
        private Integer teacher_id;
        private LocalDate session_date;
        private LocalTime start_time;
        private LocalTime end_time;
        private String topic;
        private String teacher_name;
        private String course_name;
        private String meeting_link;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DiscussionCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;

        private Integer lesson_id;
        private Integer parent_id;

        @NotBlank(message = "Discussion message cannot be empty")
        private String message;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DiscussionUpdateRequest {
        @NotBlank(message = "Discussion message cannot be empty")
        private String message;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DiscussionResponse {
        private Integer discussion_id;
        private Integer course_id;
        private Integer lesson_id;
        private String sender_uid;
        private Integer parent_id;
        private String message;
        private String sender_name;
        private String sender_role;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnnouncementCreateRequest {
        @NotNull(message = "Course ID cannot be null")
        private Integer course_id;

        private Integer session_id;

        @NotBlank(message = "Title cannot be empty")
        @Size(min = 2, max = 150, message = "Title must be between 2 and 150 characters")
        private String title;

        @NotBlank(message = "Announcement message cannot be empty")
        private String message;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnnouncementUpdateRequest {
        private String title;
        private String message;
    }

    @Getter
    @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnnouncementResponse {
        private Integer announcement_id;
        private Integer course_id;
        private Integer session_id;
        private String title;
        private String message;
    }
}
