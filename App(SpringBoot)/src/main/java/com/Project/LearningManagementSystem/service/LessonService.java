package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.LessonDtos.LessonContentCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonContentResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonDetailResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonResponse;
import com.Project.LearningManagementSystem.dto.LessonDtos.LessonUpdateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.ResourceCreateRequest;
import com.Project.LearningManagementSystem.dto.LessonDtos.ResourceResponse;
import com.Project.LearningManagementSystem.entity.Lesson;
import com.Project.LearningManagementSystem.entity.LessonContent;
import com.Project.LearningManagementSystem.entity.Resource;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.LessonContentRepository;
import com.Project.LearningManagementSystem.repository.LessonRepository;
import com.Project.LearningManagementSystem.repository.ModuleRepository;
import com.Project.LearningManagementSystem.repository.ResourceRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class LessonService {

    private final LessonRepository lessonRepository;
    private final ModuleRepository moduleRepository;
    private final LessonContentRepository contentRepository;
    private final ResourceRepository resourceRepository;

    public LessonResponse toLessonResponse(Lesson l) {
        return new LessonResponse(
                l.getLessonId(),
                l.getModuleId(),
                l.getLessonTitle(),
                l.isPublished());
    }

    @Cacheable(value = "lessonDetails", key = "#lessonId")
    public LessonDetailResponse getLessonDetail(Integer lessonId) {
        Lesson l = lessonRepository.findById(lessonId)
                .orElseThrow(() -> new ResourceNotFoundException("Lesson not found: " + lessonId));

        List<LessonContentResponse> contents = contentRepository.findByLessonIdOrderBySequenceNumberAsc(lessonId)
                .stream()
                .map(c -> new LessonContentResponse(
                        c.getContentId(), c.getLessonId(), c.getContentType(), c.getContent(), c.getSequenceNumber()))
                .toList();

        List<ResourceResponse> resources = resourceRepository.findByLessonId(lessonId).stream()
                .map(r -> new ResourceResponse(
                        r.getResourceId(), r.getLessonId(), r.getResourceName(), r.getResourceType(),
                        r.getResourceUrl()))
                .toList();

        return new LessonDetailResponse(
                l.getLessonId(),
                l.getModuleId(),
                l.getLessonTitle(),
                l.isPublished(),
                contents,
                resources);
    }

    @Cacheable(value = "lessons", key = "#moduleId")
    public List<LessonResponse> getLessonsByModule(Integer moduleId) {
        return lessonRepository.findByModuleIdOrderByLessonIdAsc(moduleId).stream().map(this::toLessonResponse)
                .toList();
    }

    @Transactional
    @CacheEvict(value = {"lessons", "lessonDetails"}, allEntries = true)
    public LessonResponse createLesson(LessonCreateRequest request) {
        if (!moduleRepository.existsById(request.getModule_id())) {
            throw new ResourceNotFoundException("Module not found: " + request.getModule_id());
        }

        Lesson lesson = new Lesson();
        lesson.setModuleId(request.getModule_id());
        lesson.setLessonTitle(request.getLesson_title().trim());
        lesson.setPublished(request.is_published());
        lesson.setCreatedAt(LocalDateTime.now());
        lessonRepository.save(lesson);

        return toLessonResponse(lesson);
    }

    @Transactional
    @CacheEvict(value = {"lessons", "lessonDetails"}, allEntries = true)
    public LessonResponse updateLesson(Integer lessonId, LessonUpdateRequest request) {
        Lesson lesson = lessonRepository.findById(lessonId)
                .orElseThrow(() -> new ResourceNotFoundException("Lesson not found: " + lessonId));

        if (request.getLesson_title() != null && !request.getLesson_title().isBlank()) {
            lesson.setLessonTitle(request.getLesson_title().trim());
        }
        if (request.getIs_published() != null) {
            lesson.setPublished(request.getIs_published());
        }
        lesson.setUpdatedAt(LocalDateTime.now());
        lessonRepository.save(lesson);

        return toLessonResponse(lesson);
    }

    @Transactional
    @CacheEvict(value = {"lessons", "lessonDetails"}, allEntries = true)
    public void deleteLesson(Integer lessonId) {
        if (!lessonRepository.existsById(lessonId)) {
            throw new ResourceNotFoundException("Lesson not found: " + lessonId);
        }
        lessonRepository.deleteById(lessonId);
    }

    @Transactional
    @CacheEvict(value = {"lessons", "lessonDetails"}, allEntries = true)
    public LessonContentResponse addLessonContent(LessonContentCreateRequest request) {
        if (!lessonRepository.existsById(request.getLesson_id())) {
            throw new ResourceNotFoundException("Lesson not found: " + request.getLesson_id());
        }

        LessonContent content = new LessonContent();
        content.setLessonId(request.getLesson_id());
        content.setContentType(request.getContent_type());
        content.setContent(request.getContent());
        content.setSequenceNumber(request.getSequence_number());
        content.setCreatedAt(LocalDateTime.now());
        contentRepository.save(content);

        return new LessonContentResponse(
                content.getContentId(), content.getLessonId(), content.getContentType(),
                content.getContent(), content.getSequenceNumber());
    }

    @Transactional
    @CacheEvict(value = {"lessons", "lessonDetails"}, allEntries = true)
    public ResourceResponse addResource(ResourceCreateRequest request) {
        if (!lessonRepository.existsById(request.getLesson_id())) {
            throw new ResourceNotFoundException("Lesson not found: " + request.getLesson_id());
        }

        Resource resource = new Resource();
        resource.setLessonId(request.getLesson_id());
        resource.setResourceName(request.getResource_name().trim());
        resource.setResourceType(request.getResource_type());
        resource.setResourceUrl(request.getResource_url());
        resource.setCreatedAt(LocalDateTime.now());
        resourceRepository.save(resource);

        return new ResourceResponse(
                resource.getResourceId(), resource.getLessonId(), resource.getResourceName(),
                resource.getResourceType(), resource.getResourceUrl());
    }
}
