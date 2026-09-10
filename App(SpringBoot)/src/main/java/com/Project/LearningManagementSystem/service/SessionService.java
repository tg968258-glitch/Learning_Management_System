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
    private final CourseAccessService courseAccessService;

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

    public List<ClassSessionResponse> getAllSessions(Integer courseId) {
        if (courseId != null) {
            return getSessionsByCourse(courseId);
        }
        return sessionRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Cacheable(value = "sessions", key = "#courseId")
    public List<ClassSessionResponse> getSessionsByCourse(Integer courseId) {
        return sessionRepository.findByCourseId(courseId).stream().map(this::toResponse).toList();
    }

    public ClassSessionResponse getSessionById(Integer sessionId) {
        ClassSession s = sessionRepository.findById(sessionId)
            .orElseThrow(() -> new ResourceNotFoundException("Session not found: " + sessionId));
        return toResponse(s);
    }

    @Transactional
    @CacheEvict(value = "sessions", allEntries = true)
    public ClassSessionResponse createSession(ClassSessionCreateRequest request, String teacherUid) {
        if (!courseRepository.existsById(request.getCourse_id())) {
            throw new ResourceNotFoundException("Course not found: " + request.getCourse_id());
        }
        Integer teacherId = courseAccessService.requireAssignedTeacher(teacherUid, request.getCourse_id());

        ClassSession s = new ClassSession();
        s.setCourseId(request.getCourse_id());
        s.setTeacherId(teacherId);
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
    public ClassSessionResponse updateSession(Integer sessionId, ClassSessionUpdateRequest request, String teacherUid) {
        ClassSession s = sessionRepository.findById(sessionId)
            .orElseThrow(() -> new ResourceNotFoundException("Session not found: " + sessionId));
        courseAccessService.requireAssignedTeacher(teacherUid, s.getCourseId());

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
    public void deleteSession(Integer sessionId, String teacherUid) {
        ClassSession session = sessionRepository.findById(sessionId)
            .orElseThrow(() -> new ResourceNotFoundException("Session not found: " + sessionId));
        courseAccessService.requireAssignedTeacher(teacherUid, session.getCourseId());
        sessionRepository.deleteById(sessionId);
    }
}
