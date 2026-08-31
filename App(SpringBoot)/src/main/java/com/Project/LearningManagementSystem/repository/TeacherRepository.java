package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Teacher;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TeacherRepository extends JpaRepository<Teacher, Integer> {
    Optional<Teacher> findByUid(String uid);
    boolean existsByUid(String uid);
}
