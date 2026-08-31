package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.QuestionOption;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface QuestionOptionRepository extends JpaRepository<QuestionOption, Integer> {
    List<QuestionOption> findByQuestionId(Integer questionId);
}
