package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Module;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ModuleRepository extends JpaRepository<Module, Integer> {
    List<Module> findByCourseIdOrderByModuleIdAsc(Integer courseId);
}
