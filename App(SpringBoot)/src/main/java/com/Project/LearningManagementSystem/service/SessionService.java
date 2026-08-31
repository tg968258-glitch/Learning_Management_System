package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.ClassSessionUpdateRequest;
import com.Project.LearningManagementSystem.entity.ClassSession;
import com.Project.LearningManagementSystem.entity.Course;
import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.ClassSessionRepository;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class SessionService {

    private final ClassSessionRepository sessionRepository;
    private final CourseRepository courseRepository;
    private final TeacherRepository teacherRepository;

    public ClassSessionResponse toResponse(ClassSession s) {
        String teacherName = s.getTeacherId() != null ?
            teacherRepository.findById(s.getTeacherId()).map(Teacher::getName).orElse(null) : null;
        String courseName = courseRepository.findById(s.getCourseId()).map(Course::getCourseName).orElse(null);

        return new ClassSessionResponse(
            s.getSessionId(),
            s.getCourseId(),
            s.getTeacherId(),
            s.getSessionDate(),
            s.getStartTime(),
            s.getEndTime(),
            s.getTopic(),
            teacherName,
            courseName,
            s.getMeetingLink()
        );
    }

    @Cacheable(value = "sessions", key = "#courseId")
    public List<ClassSessionResponse> getSessionsByCourse(Integer courseId) {
        return sessionRepository.findByCourseId(courseId).stream().map(this::toResponse).toList();
    }

    @Transactional
    @CacheEvict(value = "sessions", allEntries = true)
    public ClassSessionResponse createSession(ClassSessionCreateRequest request) {
        if (!courseRepository.existsById(request.getCourse_id())) {
            throw new ResourceNotFoundException("Course not found: " + request.getCourse_id());
        }

        ClassSession s = new ClassSession();
        s.setCourseId(request.getCourse_id());
        s.setTeacherId(request.getTeacher_id());
        s.setSessionDate(request.getSession_date());
        s.setStartTime(request.getStart_time());
        s.setEndTime(request.getEnd_time());
        s.setTopic(request.getTopic());
        s.setMeetingLink(request.getMeeting_link() != null ? request.getMeeting_link().trim() : null);
        sessionRepository.save(s);

        return toResponse(s);
    }

    @Transactional
    @CacheEvict(value = "sessions", allEntries = true)
    public ClassSessionResponse updateSession(Integer sessionId, ClassSessionUpdateRequest request) {
        ClassSession s = sessionRepository.findById(sessionId)
            .orElseThrow(() -> new ResourceNotFoundException("Session not found: " + sessionId));

        if (request.getTeacher_id() != null) {
            s.setTeacherId(request.getTeacher_id());
        }
        if (request.getSession_date() != null) {
            s.setSessionDate(request.getSession_date());
        }
        if (request.getStart_time() != null) {
            s.setStartTime(request.getStart_time());
        }
        if (request.getEnd_time() != null) {
            s.setEndTime(request.getEnd_time());
        }
        if (request.getTopic() != null) {
            s.setTopic(request.getTopic());
        }
        if (request.getMeeting_link() != null) {
            s.setMeetingLink(request.getMeeting_link().trim().isEmpty() ? null : request.getMeeting_link().trim());
        }
        sessionRepository.save(s);

        return toResponse(s);
    }

    @Transactional
    @CacheEvict(value = "sessions", allEntries = true)
    public void deleteSession(Integer sessionId) {
        if (!sessionRepository.existsById(sessionId)) {
            throw new ResourceNotFoundException("Session not found: " + sessionId);
        }
        sessionRepository.deleteById(sessionId);
    }
}
