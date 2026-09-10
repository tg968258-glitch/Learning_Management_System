package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.CourseDtos.CourseCreateRequest;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseResponse;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseLessonInfo;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseModuleInfo;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseTeacherInfo;
import com.Project.LearningManagementSystem.dto.CourseDtos.CourseUpdateRequest;
import com.Project.LearningManagementSystem.dto.ProgressDtos.CourseProgressSummaryResponse;
import com.Project.LearningManagementSystem.entity.Course;
import com.Project.LearningManagementSystem.entity.CourseTeacher;
import com.Project.LearningManagementSystem.entity.CourseTeacherId;
import com.Project.LearningManagementSystem.entity.Lesson;
import com.Project.LearningManagementSystem.entity.Module;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.CourseTeacherRepository;
import com.Project.LearningManagementSystem.repository.EnrollmentRepository;
import com.Project.LearningManagementSystem.repository.LessonRepository;
import com.Project.LearningManagementSystem.repository.ModuleRepository;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import java.time.LocalDateTime;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CourseService {

    private final CourseRepository courseRepository;
    private final CourseTeacherRepository courseTeacherRepository;
    private final TeacherRepository teacherRepository;
    private final StudentRepository studentRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final ModuleRepository moduleRepository;
    private final LessonRepository lessonRepository;
    private final ProgressService progressService;

    public CourseResponse toResponse(Course course) {
        return toResponse(course, null, false);
    }

    public CourseResponse toResponse(Course course, Integer studentId, boolean includeModules) {
        List<CourseTeacher> links = courseTeacherRepository.findByIdCourseId(course.getCourseId());
        List<CourseTeacherInfo> teachers = new ArrayList<>();
        for (CourseTeacher link : links) {
            teacherRepository.findById(link.getId().getTeacherId()).ifPresent(t -> {
                teachers.add(new CourseTeacherInfo(t.getTeacherId(), t.getName(), t.getSpecialization()));
            });
        }

        List<Module> courseModules = moduleRepository.findByCourseIdOrderByModuleIdAsc(course.getCourseId());
        List<CourseModuleInfo> moduleDetails = new ArrayList<>();
        int lessonCount = 0;
        for (Module module : courseModules) {
            List<Lesson> lessons = lessonRepository.findByModuleIdOrderByLessonIdAsc(module.getModuleId());
            lessonCount += lessons.size();
            if (includeModules) {
                List<CourseLessonInfo> lessonDetails = lessons.stream()
                    .map(lesson -> new CourseLessonInfo(
                        lesson.getLessonId(),
                        lesson.getModuleId(),
                        lesson.getLessonTitle(),
                        lesson.isPublished()))
                    .toList();
                moduleDetails.add(new CourseModuleInfo(
                    module.getModuleId(),
                    module.getCourseId(),
                    module.getModuleName(),
                    module.getDescription(),
                    module.isPublished(),
                    lessonDetails));
            }
        }

        long enrollmentCount = enrollmentRepository.findByCourseId(course.getCourseId()).stream()
            .filter(enrollment -> "active".equalsIgnoreCase(enrollment.getStatus()))
            .count();
        boolean isEnrolled = studentId != null && enrollmentRepository
            .findByStudentIdAndCourseId(studentId, course.getCourseId())
            .filter(enrollment -> "active".equalsIgnoreCase(enrollment.getStatus()))
            .isPresent();
        Integer completedLessons = null;
        BigDecimal progressPercentage = null;
        if (isEnrolled) {
            CourseProgressSummaryResponse progress = progressService.getCourseProgressSummary(studentId, course.getCourseId());
            completedLessons = progress.getCompleted_lessons();
            progressPercentage = progress.getOverall_progress_percentage();
        }

        return new CourseResponse(
                course.getCourseId(),
                course.getCourseName(),
                course.getDescription(),
                course.getDuration(),
                course.getStatus(),
                course.getCategory(),
                teachers,
                moduleDetails,
                courseModules.size(),
                lessonCount,
                enrollmentCount,
                isEnrolled,
                completedLessons,
                progressPercentage);
    }

    public List<CourseResponse> getAllCourses() {
        return courseRepository.findAll().stream().map(this::toResponse).toList();
    }

    public List<CourseResponse> getMyCourses(String uid, String role) {
        if ("TEACHER".equalsIgnoreCase(role)) {
            Teacher teacher = teacherRepository.findByUid(uid)
                    .orElseThrow(() -> new ResourceNotFoundException("Teacher profile not found"));
            return courseTeacherRepository.findByIdTeacherId(teacher.getTeacherId()).stream()
                    .map(link -> courseRepository.findById(link.getId().getCourseId()))
                    .flatMap(java.util.Optional::stream)
                    .map(this::toResponse)
                    .toList();
        }

        if ("STUDENT".equalsIgnoreCase(role)) {
            Student student = studentRepository.findByUid(uid)
                    .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
            return enrollmentRepository.findByStudentId(student.getStudentId()).stream()
                    .filter(enrollment -> !"dropped".equalsIgnoreCase(enrollment.getStatus()))
                    .map(enrollment -> courseRepository.findById(enrollment.getCourseId()))
                    .flatMap(java.util.Optional::stream)
                    .map(course -> toResponse(course, student.getStudentId(), false))
                    .toList();
        }

        throw new BadRequestException("My courses is only available to students and teachers");
    }

    public CourseResponse getCourseById(Integer courseId, String uid, String role) {
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Course not found: " + courseId));
        Integer studentId = null;
        if ("STUDENT".equalsIgnoreCase(role)) {
            studentId = studentRepository.findByUid(uid)
                .map(Student::getStudentId)
                .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        }
        return toResponse(course, studentId, true);
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
