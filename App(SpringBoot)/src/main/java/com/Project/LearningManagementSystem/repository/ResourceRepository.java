package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Resource;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface ResourceRepository extends JpaRepository<Resource, Integer> {
    List<Resource> findByLessonId(Integer lessonId);

    @Query("SELECT r FROM Resource r WHERE r.lessonId IN (SELECT l.lessonId FROM Lesson l WHERE l.moduleId IN (SELECT m.moduleId FROM Module m WHERE m.courseId = :courseId))")
    List<Resource> findByCourseId(@Param("courseId") Integer courseId);
}
