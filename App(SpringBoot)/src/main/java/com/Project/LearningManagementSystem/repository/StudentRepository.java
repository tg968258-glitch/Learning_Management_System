package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Student;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface StudentRepository extends JpaRepository<Student, Integer> {
    Optional<Student> findByUid(String uid);
    boolean existsByUid(String uid);
}
