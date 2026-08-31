package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.QuizQuestion;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface QuizQuestionRepository extends JpaRepository<QuizQuestion, Integer> {
    List<QuizQuestion> findByQuizId(Integer quizId);
    List<QuizQuestion> findByQuizIdOrderByQuestionIdAsc(Integer quizId);
}
