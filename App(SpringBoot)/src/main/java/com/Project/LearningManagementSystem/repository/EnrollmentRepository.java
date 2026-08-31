package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Enrollment;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EnrollmentRepository extends JpaRepository<Enrollment, Integer> {
    Optional<Enrollment> findByStudentIdAndCourseId(Integer studentId, Integer courseId);
    List<Enrollment> findByStudentId(Integer studentId);
    List<Enrollment> findByCourseId(Integer courseId);
    boolean existsByStudentIdAndCourseId(Integer studentId, Integer courseId);
}
