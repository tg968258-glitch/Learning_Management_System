package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.AnnouncementUpdateRequest;
import com.Project.LearningManagementSystem.entity.Announcement;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.AnnouncementRepository;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AnnouncementService {

    private final AnnouncementRepository announcementRepository;
    private final CourseRepository courseRepository;

    public AnnouncementResponse toResponse(Announcement a) {
        return new AnnouncementResponse(
                a.getAnnouncementId(),
                a.getCourseId(),
                a.getSessionId(),
                a.getTitle(),
                a.getMessage());
    }

    @Cacheable(value = "announcements", key = "#courseId")
    public List<AnnouncementResponse> getAnnouncementsByCourse(Integer courseId) {
        return announcementRepository.findByCourseIdOrderByCreatedAtDesc(courseId).stream().map(this::toResponse)
                .toList();
    }

    @Transactional
    @CacheEvict(value = "announcements", allEntries = true)
    public AnnouncementResponse createAnnouncement(AnnouncementCreateRequest request, String createdByUid) {
        if (!courseRepository.existsById(request.getCourse_id())) {
            throw new ResourceNotFoundException("Course not found: " + request.getCourse_id());
        }

        Announcement a = new Announcement();
        a.setCourseId(request.getCourse_id());
        a.setSessionId(request.getSession_id());
        a.setTitle(request.getTitle().trim());
        a.setMessage(request.getMessage().trim());
        a.setCreatedBy(createdByUid);
        a.setCreatedAt(LocalDateTime.now());
        announcementRepository.save(a);

        return toResponse(a);
    }

    @Transactional
    @CacheEvict(value = "announcements", allEntries = true)
    public AnnouncementResponse updateAnnouncement(Integer announcementId, AnnouncementUpdateRequest request) {
        Announcement a = announcementRepository.findById(announcementId)
                .orElseThrow(() -> new ResourceNotFoundException("Announcement not found: " + announcementId));

        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            a.setTitle(request.getTitle().trim());
        }
        if (request.getMessage() != null && !request.getMessage().isBlank()) {
            a.setMessage(request.getMessage().trim());
        }
        a.setUpdatedAt(LocalDateTime.now());
        announcementRepository.save(a);

        return toResponse(a);
    }

    @Transactional
    @CacheEvict(value = "announcements", allEntries = true)
    public void deleteAnnouncement(Integer announcementId) {
        if (!announcementRepository.existsById(announcementId)) {
            throw new ResourceNotFoundException("Announcement not found: " + announcementId);
        }
        announcementRepository.deleteById(announcementId);
    }
}
