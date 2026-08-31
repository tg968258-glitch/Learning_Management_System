package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import java.io.Serializable;
import java.util.Objects;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Embeddable
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class CourseTeacherId implements Serializable {

    @Column(name = "course_id")
    private Integer courseId;

    @Column(name = "teacher_id")
    private Integer teacherId;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof CourseTeacherId)) return false;
        CourseTeacherId that = (CourseTeacherId) o;
        return Objects.equals(courseId, that.courseId) && Objects.equals(teacherId, that.teacherId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(courseId, teacherId);
    }
}
