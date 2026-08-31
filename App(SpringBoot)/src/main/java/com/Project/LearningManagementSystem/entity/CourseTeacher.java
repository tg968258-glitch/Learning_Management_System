package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "course_teachers")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class CourseTeacher {

    @EmbeddedId
    private CourseTeacherId id;

    @Column(name = "is_course_admin", nullable = false)
    private boolean isCourseAdmin = false;
}
