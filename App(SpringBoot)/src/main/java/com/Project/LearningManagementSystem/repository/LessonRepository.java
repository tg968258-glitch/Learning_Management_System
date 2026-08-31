package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Lesson;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LessonRepository extends JpaRepository<Lesson, Integer> {
    List<Lesson> findByModuleIdOrderByLessonIdAsc(Integer moduleId);
}
