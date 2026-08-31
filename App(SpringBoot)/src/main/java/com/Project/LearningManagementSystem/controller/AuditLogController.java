package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.NotificationDtos.AuditLogResponse;
import com.Project.LearningManagementSystem.entity.AuditLog;
import com.Project.LearningManagementSystem.service.AuditService;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/audit-logs")
@Tag(name = "Audit Logs")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class AuditLogController {

    private final AuditService auditService;

    @GetMapping("/")
    public ResponseEntity<List<AuditLogResponse>> listAuditLogs(
            @RequestParam(required = false) String uid,
            @RequestParam(required = false) String entity_type,
            @RequestParam(required = false, defaultValue = "100") int limit) {
        List<AuditLog> logs = auditService.getAllAuditLogs();
        List<AuditLogResponse> response = logs.stream()
                .limit(limit)
                .map(l -> new AuditLogResponse(l.getAuditId(), l.getUid(), l.getAction(), l.getEntityType(),
                        l.getEntityId()))
                .toList();
        return ResponseEntity.ok(response);
    }
}
