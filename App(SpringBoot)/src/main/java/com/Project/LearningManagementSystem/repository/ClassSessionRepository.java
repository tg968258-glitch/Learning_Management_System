package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.ClassSession;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ClassSessionRepository extends JpaRepository<ClassSession, Integer> {
    List<ClassSession> findByCourseId(Integer courseId);
    List<ClassSession> findByTeacherId(Integer teacherId);
}
