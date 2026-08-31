package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.entity.AuditLog;
import com.Project.LearningManagementSystem.repository.AuditLogRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    public void logAction(String uid, String action, String entityType, String entityId) {
        AuditLog log = new AuditLog();
        log.setUid(uid);
        log.setAction(action);
        log.setEntityType(entityType);
        log.setEntityId(entityId);
        log.setCreatedAt(LocalDateTime.now());
        auditLogRepository.save(log);
    }

    public List<AuditLog> getAllAuditLogs() {
        return auditLogRepository.findAllByOrderByCreatedAtDesc();
    }
}
