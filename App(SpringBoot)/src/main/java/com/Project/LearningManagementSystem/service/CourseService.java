package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.CourseDtos.CourseCreateRequest;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseResponse;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseTeacherInfo;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseUpdateRequest;
import com.Project.LearningManagementSystem.entity.Course;
import com.Project.LearningManagementSystem.entity.CourseTeacher;
import com.Project.LearningManagementSystem.entity.CourseTeacherId;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.CourseTeacherRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CourseService {

    private final CourseRepository courseRepository;
    private final CourseTeacherRepository courseTeacherRepository;
    private final TeacherRepository teacherRepository;

    public CourseResponse toResponse(Course course) {
        List<CourseTeacher> links = courseTeacherRepository.findByIdCourseId(course.getCourseId());
        List<CourseTeacherInfo> teachers = new ArrayList<>();
        for (CourseTeacher link : links) {
            teacherRepository.findById(link.getId().getTeacherId()).ifPresent(t -> {
                teachers.add(new CourseTeacherInfo(t.getTeacherId(), t.getName(), t.getSpecialization()));
            });
        }

        return new CourseResponse(
                course.getCourseId(),
                course.getCourseName(),
                course.getDescription(),
                course.getDuration(),
                course.getStatus(),
                course.getCategory(),
                teachers);
    }

    @Cacheable(value = "courses", key = "'all'")
    public List<CourseResponse> getAllCourses() {
        return courseRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Cacheable(value = "courses", key = "#courseId")
    public CourseResponse getCourseById(Integer courseId) {
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Course not found: " + courseId));
        return toResponse(course);
    }

    @Transactional
    @CacheEvict(value = "courses", allEntries = true)
    public CourseResponse createCourse(CourseCreateRequest request, String createdByUid) {
        Course course = new Course();
        course.setCourseName(request.getCourse_name().trim());
        course.setDescription(request.getDescription());
        course.setDuration(request.getDuration());
        course.setStatus(request.getStatus() != null ? request.getStatus().toLowerCase() : "draft");
        course.setCategory(request.getCategory());
        course.setCreatedBy(createdByUid);
        course.setCreatedAt(LocalDateTime.now());
        courseRepository.save(course);
        return toResponse(course);
    }

    @Transactional
    @CacheEvict(value = "courses", allEntries = true)
    public CourseResponse updateCourse(Integer courseId, CourseUpdateRequest request) {
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Course not found: " + courseId));

        if (request.getCourse_name() != null && !request.getCourse_name().isBlank()) {
            course.setCourseName(request.getCourse_name().trim());
        }
        if (request.getDescription() != null) {
            course.setDescription(request.getDescription());
        }
        if (request.getDuration() != null) {
            course.setDuration(request.getDuration());
        }
        if (request.getStatus() != null) {
            course.setStatus(request.getStatus().toLowerCase());
        }
        if (request.getCategory() != null) {
            course.setCategory(request.getCategory());
        }
        course.setUpdatedAt(LocalDateTime.now());
        courseRepository.save(course);
        return toResponse(course);
    }

    @Transactional
    @CacheEvict(value = "courses", allEntries = true)
    public void deleteCourse(Integer courseId) {
        if (!courseRepository.existsById(courseId)) {
            throw new ResourceNotFoundException("Course not found: " + courseId);
        }
        courseRepository.deleteById(courseId);
    }

    @Transactional
    @CacheEvict(value = "courses", allEntries = true)
    public CourseResponse assignTeachers(Integer courseId, List<Integer> teacherIds) {
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Course not found: " + courseId));

        for (Integer teacherId : teacherIds) {
            if (!teacherRepository.existsById(teacherId)) {
                throw new BadRequestException("Teacher with ID " + teacherId + " does not exist");
            }
            if (!courseTeacherRepository.existsByIdCourseIdAndIdTeacherId(courseId, teacherId)) {
                CourseTeacher link = new CourseTeacher(new CourseTeacherId(courseId, teacherId), false);
                courseTeacherRepository.save(link);
            }
        }
        return toResponse(course);
    }
}
