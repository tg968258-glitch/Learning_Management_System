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
public class LessonProgressId implements Serializable {

    @Column(name = "student_id")
    private Integer studentId;

    @Column(name = "lesson_id")
    private Integer lessonId;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof LessonProgressId)) return false;
        LessonProgressId that = (LessonProgressId) o;
        return Objects.equals(studentId, that.studentId) && Objects.equals(lessonId, that.lessonId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(studentId, lessonId);
    }
}
