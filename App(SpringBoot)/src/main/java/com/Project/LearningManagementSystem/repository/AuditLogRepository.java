package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.AuditLog;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Integer> {
    List<AuditLog> findByUidOrderByCreatedAtDesc(String uid);
    List<AuditLog> findByEntityTypeOrderByCreatedAtDesc(String entityType);
    List<AuditLog> findAllByOrderByCreatedAtDesc();
}
