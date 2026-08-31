package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Assignment;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AssignmentRepository extends JpaRepository<Assignment, Integer> {
    List<Assignment> findByCourseId(Integer courseId);
}
