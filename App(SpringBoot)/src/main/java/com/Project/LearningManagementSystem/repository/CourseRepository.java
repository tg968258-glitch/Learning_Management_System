package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Course;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CourseRepository extends JpaRepository<Course, Integer> {
    List<Course> findByCategory(String category);
    List<Course> findByStatus(String status);
    List<Course> findByCreatedBy(String createdBy);
}
