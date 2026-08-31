package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleCreateRequest;
import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleResponse;
import com.Project.LearningManagementSystem.dto.ModuleDtos.ModuleUpdateRequest;
import com.Project.LearningManagementSystem.entity.Module;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.ModuleRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ModuleService {

    private final ModuleRepository moduleRepository;
    private final CourseRepository courseRepository;

    public ModuleResponse toResponse(Module m) {
        return new ModuleResponse(
                m.getModuleId(),
                m.getCourseId(),
                m.getModuleName(),
                m.getDescription(),
                m.isPublished(),
                m.getPublishedBy());
    }

    @Cacheable(value = "modules", key = "#courseId")
    public List<ModuleResponse> getModulesByCourse(Integer courseId) {
        return moduleRepository.findByCourseIdOrderByModuleIdAsc(courseId).stream().map(this::toResponse).toList();
    }

    @Transactional
    @CacheEvict(value = "modules", allEntries = true)
    public ModuleResponse createModule(ModuleCreateRequest request, String uid) {
        if (!courseRepository.existsById(request.getCourse_id())) {
            throw new ResourceNotFoundException("Course not found: " + request.getCourse_id());
        }

        Module module = new Module();
        module.setCourseId(request.getCourse_id());
        module.setModuleName(request.getModule_name().trim());
        module.setDescription(request.getDescription());
        module.setPublished(request.is_published());
        if (request.is_published()) {
            module.setPublishedBy(uid);
        }
        moduleRepository.save(module);
        return toResponse(module);
    }

    @Transactional
    @CacheEvict(value = "modules", allEntries = true)
    public ModuleResponse updateModule(Integer moduleId, ModuleUpdateRequest request, String uid) {
        Module module = moduleRepository.findById(moduleId)
                .orElseThrow(() -> new ResourceNotFoundException("Module not found: " + moduleId));

        if (request.getModule_name() != null && !request.getModule_name().isBlank()) {
            module.setModuleName(request.getModule_name().trim());
        }
        if (request.getDescription() != null) {
            module.setDescription(request.getDescription());
        }
        if (request.getIs_published() != null) {
            module.setPublished(request.getIs_published());
            if (request.getIs_published()) {
                module.setPublishedBy(uid);
            }
        }

        moduleRepository.save(module);
        return toResponse(module);
    }

    @Transactional
    @CacheEvict(value = "modules", allEntries = true)
    public void deleteModule(Integer moduleId) {
        if (!moduleRepository.existsById(moduleId)) {
            throw new ResourceNotFoundException("Module not found: " + moduleId);
        }
        moduleRepository.deleteById(moduleId);
    }
}
