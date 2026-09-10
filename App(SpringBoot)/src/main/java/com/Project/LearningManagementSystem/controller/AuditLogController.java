package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.NotificationDtos.AuditLogResponse;
import com.Project.LearningManagementSystem.dto.NotificationDtos.AuditLogPageResponse;
import com.Project.LearningManagementSystem.entity.AuditLog;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.repository.UserRepository;
import com.Project.LearningManagementSystem.service.AuditService;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/audit-logs")
@Tag(name = "Audit Logs")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class AuditLogController {

    private final AuditService auditService;
    private final UserRepository userRepository;

    @GetMapping("/")
    public ResponseEntity<AuditLogPageResponse> listAuditLogs(
            @RequestParam(required = false) String uid,
            @RequestParam(required = false) String entity_type,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from_date,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to_date,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size) {
        if (page < 1 || page_size < 1 || page_size > 100) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid pagination parameters.");
        }
        if (from_date != null && to_date != null && from_date.isAfter(to_date)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "From Date cannot be later than To Date.");
        }

        Page<AuditLog> result = auditService.getAuditLogs(uid, entity_type, from_date, to_date, page, page_size);
        Map<String, User> users = userRepository.findAllById(
                        result.getContent().stream().map(AuditLog::getUid).distinct().toList())
                .stream()
                .collect(Collectors.toMap(User::getUid, Function.identity()));
        List<AuditLogResponse> response = result.getContent().stream()
                .map(log -> {
                    User user = users.get(log.getUid());
                    return new AuditLogResponse(
                            log.getAuditId(),
                            log.getUid(),
                            log.getAction(),
                            log.getEntityType(),
                            log.getEntityId(),
                            user != null ? user.getUsername() : "System",
                            user != null ? user.getRole() : "system",
                            "success",
                            log.getCreatedAt());
                })
                .toList();
        return ResponseEntity.ok(new AuditLogPageResponse(
                response, page, page_size, result.getTotalElements(), result.getTotalPages()));
    }
}
