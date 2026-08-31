package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleCreateRequest;
import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleResponse;
import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleUpdateRequest;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.ModuleService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/modules")
@Tag(name = "Modules")
@RequiredArgsConstructor
public class ModuleController {

    private final ModuleService moduleService;

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<ModuleResponse>> listCourseModules(
        @PathVariable Integer course_id,
        @RequestParam(required = false, defaultValue = "false") boolean published_only,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        return ResponseEntity.ok(moduleService.getModulesByCourse(course_id));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ModuleResponse> addModule(
        @Valid @RequestBody ModuleCreateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(moduleService.createModule(request, currentUser.getUid()));
    }

    @PutMapping("/{module_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<ModuleResponse> updateModule(
        @PathVariable Integer module_id,
        @Valid @RequestBody ModuleUpdateRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        return ResponseEntity.ok(moduleService.updateModule(module_id, request, currentUser.getUid()));
    }

    @DeleteMapping("/{module_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> removeModule(@PathVariable Integer module_id) {
        moduleService.deleteModule(module_id);
        return ResponseEntity.ok(Map.of("message", "Module deleted successfully"));
    }
}
