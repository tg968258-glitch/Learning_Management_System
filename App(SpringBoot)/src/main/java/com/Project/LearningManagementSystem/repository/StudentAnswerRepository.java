package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.StudentAnswer;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface StudentAnswerRepository extends JpaRepository<StudentAnswer, Integer> {
    List<StudentAnswer> findByAttemptId(Integer attemptId);
    Optional<StudentAnswer> findByAttemptIdAndQuestionId(Integer attemptId, Integer questionId);
}
