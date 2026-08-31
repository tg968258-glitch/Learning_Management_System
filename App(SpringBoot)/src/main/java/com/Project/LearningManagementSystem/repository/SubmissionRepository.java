package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Submission;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SubmissionRepository extends JpaRepository<Submission, Integer> {
    List<Submission> findByAssignmentId(Integer assignmentId);
    List<Submission> findByStudentId(Integer studentId);
    Optional<Submission> findByAssignmentIdAndStudentId(Integer assignmentId, Integer studentId);
    boolean existsByAssignmentIdAndStudentId(Integer assignmentId, Integer studentId);
}
