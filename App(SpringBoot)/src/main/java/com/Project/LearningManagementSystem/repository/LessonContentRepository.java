package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.LessonContent;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LessonContentRepository extends JpaRepository<LessonContent, Integer> {
    List<LessonContent> findByLessonIdOrderBySequenceNumberAsc(Integer lessonId);
}
