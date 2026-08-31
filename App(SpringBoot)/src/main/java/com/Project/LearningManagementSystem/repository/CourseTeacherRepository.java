package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.CourseTeacher;
import com.Project.LearningManagementSystem.entity.CourseTeacherId;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CourseTeacherRepository extends JpaRepository<CourseTeacher, CourseTeacherId> {
    List<CourseTeacher> findByIdCourseId(Integer courseId);

    List<CourseTeacher> findByIdTeacherId(Integer teacherId);

    boolean existsByIdCourseIdAndIdTeacherId(Integer courseId, Integer teacherId);

    void deleteByIdCourseIdAndIdTeacherId(Integer courseId, Integer teacherId);
}
