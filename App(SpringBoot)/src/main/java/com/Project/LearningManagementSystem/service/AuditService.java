package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.entity.AuditLog;
import com.Project.LearningManagementSystem.repository.AuditLogRepository;
import java.time.LocalDateTime;
import java.time.LocalDate;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;

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

    public Page<AuditLog> getAuditLogs(
            String uid,
            String entityType,
            LocalDate fromDate,
            LocalDate toDate,
            int page,
            int pageSize) {
        Specification<AuditLog> filters = Specification.where(null);
        if (uid != null && !uid.isBlank()) {
            filters = filters.and((root, query, cb) -> cb.equal(root.get("uid"), uid));
        }
        if (entityType != null && !entityType.isBlank()) {
            filters = filters.and((root, query, cb) -> cb.equal(root.get("entityType"), entityType));
        }
        if (fromDate != null) {
            filters = filters.and((root, query, cb) ->
                    cb.greaterThanOrEqualTo(root.get("createdAt"), fromDate.atStartOfDay()));
        }
        if (toDate != null) {
            filters = filters.and((root, query, cb) ->
                    cb.lessThan(root.get("createdAt"), toDate.plusDays(1).atStartOfDay()));
        }
        return auditLogRepository.findAll(
                filters,
                PageRequest.of(page - 1, pageSize, Sort.by(Sort.Direction.DESC, "createdAt")));
    }
}
