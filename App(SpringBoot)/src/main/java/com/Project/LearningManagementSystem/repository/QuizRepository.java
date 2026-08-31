package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Quiz;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface QuizRepository extends JpaRepository<Quiz, Integer> {
    List<Quiz> findByLessonId(Integer lessonId);

    @Query("SELECT q FROM Quiz q WHERE q.lessonId IN (SELECT l.lessonId FROM Lesson l WHERE l.moduleId IN (SELECT m.moduleId FROM Module m WHERE m.courseId = :courseId))")
    List<Quiz> findByCourseId(@Param("courseId") Integer courseId);
}
