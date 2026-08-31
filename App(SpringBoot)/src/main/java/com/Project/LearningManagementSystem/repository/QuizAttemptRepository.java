package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.QuizAttempt;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface QuizAttemptRepository extends JpaRepository<QuizAttempt, Integer> {
    List<QuizAttempt> findByQuizIdAndStudentId(Integer quizId, Integer studentId);
    List<QuizAttempt> findByQuizId(Integer quizId);
    List<QuizAttempt> findByStudentId(Integer studentId);
    Optional<QuizAttempt> findByQuizIdAndStudentIdAndAttemptNumber(Integer quizId, Integer studentId, Integer attemptNumber);
}
