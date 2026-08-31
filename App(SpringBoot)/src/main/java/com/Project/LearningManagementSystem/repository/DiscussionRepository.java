package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Discussion;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DiscussionRepository extends JpaRepository<Discussion, Integer> {
    List<Discussion> findByCourseIdAndParentIdIsNullOrderByCreatedAtAsc(Integer courseId);
    List<Discussion> findByParentIdOrderByCreatedAtAsc(Integer parentId);
    List<Discussion> findByCourseIdOrderByCreatedAtAsc(Integer courseId);
}
