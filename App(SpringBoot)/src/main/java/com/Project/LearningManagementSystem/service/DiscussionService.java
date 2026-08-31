package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionUpdateRequest;
import com.Project.LearningManagementSystem.entity.Discussion;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.ForbiddenException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.DiscussionRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class DiscussionService {

    private final DiscussionRepository discussionRepository;
    private final CourseRepository courseRepository;
    private final UserRepository userRepository;

    public DiscussionResponse toResponse(Discussion d) {
        User u = userRepository.findById(d.getSenderUid()).orElse(null);
        String senderName = u != null ? u.getUsername() : null;
        String senderRole = u != null ? u.getRole() : null;

        return new DiscussionResponse(
                d.getDiscussionId(),
                d.getCourseId(),
                d.getLessonId(),
                d.getSenderUid(),
                d.getParentId(),
                d.getMessage(),
                senderName,
                senderRole);
    }

    public List<DiscussionResponse> getDiscussionsByCourse(Integer courseId) {
        return discussionRepository.findByCourseIdOrderByCreatedAtAsc(courseId).stream().map(this::toResponse).toList();
    }

    @Transactional
    public DiscussionResponse createDiscussion(DiscussionCreateRequest request, String senderUid) {
        if (!courseRepository.existsById(request.getCourse_id())) {
            throw new ResourceNotFoundException("Course not found: " + request.getCourse_id());
        }

        Discussion d = new Discussion();
        d.setCourseId(request.getCourse_id());
        d.setLessonId(request.getLesson_id());
        d.setParentId(request.getParent_id());
        d.setMessage(request.getMessage().trim());
        d.setSenderUid(senderUid);
        d.setCreatedAt(LocalDateTime.now());
        discussionRepository.save(d);

        return toResponse(d);
    }

    @Transactional
    public DiscussionResponse updateDiscussion(Integer discussionId, DiscussionUpdateRequest request,
            String senderUid) {
        Discussion d = discussionRepository.findById(discussionId)
                .orElseThrow(() -> new ResourceNotFoundException("Discussion message not found: " + discussionId));

        if (!d.getSenderUid().equals(senderUid)) {
            throw new ForbiddenException("You can only edit your own messages");
        }

        d.setMessage(request.getMessage().trim());
        d.setUpdatedAt(LocalDateTime.now());
        discussionRepository.save(d);

        return toResponse(d);
    }

    @Transactional
    public void deleteDiscussion(Integer discussionId, String senderUid, boolean isAdmin) {
        Discussion d = discussionRepository.findById(discussionId)
                .orElseThrow(() -> new ResourceNotFoundException("Discussion message not found: " + discussionId));

        if (!isAdmin && !d.getSenderUid().equals(senderUid)) {
            throw new ForbiddenException("You can only delete your own messages");
        }

        discussionRepository.deleteById(discussionId);
    }
}
