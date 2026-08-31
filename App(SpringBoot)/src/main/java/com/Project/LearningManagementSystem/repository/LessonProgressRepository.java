package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.LessonProgress;
import com.Project.LearningManagementSystem.entity.LessonProgressId;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LessonProgressRepository extends JpaRepository<LessonProgress, LessonProgressId> {
    List<LessonProgress> findByIdStudentId(Integer studentId);
    Optional<LessonProgress> findByIdStudentIdAndIdLessonId(Integer studentId, Integer lessonId);
}
