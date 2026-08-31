package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.ProgressDtos.CourseProgressSummaryResponse;
import com.Project.LearningManagementSystem.dto.ProgressDtos.LessonProgressResponse;
import com.Project.LearningManagementSystem.dto.ProgressDtos.LessonProgressUpdateRequest;
import com.Project.LearningManagementSystem.entity.Course;
import com.Project.LearningManagementSystem.entity.Lesson;
import com.Project.LearningManagementSystem.entity.LessonProgress;
import com.Project.LearningManagementSystem.entity.LessonProgressId;
import com.Project.LearningManagementSystem.entity.Module;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.LessonProgressRepository;
import com.Project.LearningManagementSystem.repository.LessonRepository;
import com.Project.LearningManagementSystem.repository.ModuleRepository;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ProgressService {

    private final LessonProgressRepository progressRepository;
    private final LessonRepository lessonRepository;
    private final ModuleRepository moduleRepository;
    private final CourseRepository courseRepository;

    public LessonProgressResponse toResponse(LessonProgress p) {
        String lessonTitle = lessonRepository.findById(p.getId().getLessonId()).map(Lesson::getLessonTitle).orElse(null);
        return new LessonProgressResponse(
            p.getId().getStudentId(),
            p.getId().getLessonId(),
            p.getProgressPercentage(),
            p.isCompleted(),
            p.getCompletedDate(),
            lessonTitle
        );
    }

    public List<LessonProgressResponse> getStudentProgress(Integer studentId) {
        return progressRepository.findByIdStudentId(studentId).stream().map(this::toResponse).toList();
    }

    @Transactional
    public LessonProgressResponse updateLessonProgress(Integer studentId, Integer lessonId, LessonProgressUpdateRequest request) {
        if (!lessonRepository.existsById(lessonId)) {
            throw new ResourceNotFoundException("Lesson not found: " + lessonId);
        }

        LessonProgressId id = new LessonProgressId(studentId, lessonId);
        LessonProgress p = progressRepository.findById(id).orElse(new LessonProgress(id, BigDecimal.ZERO, false, null));

        p.setProgressPercentage(request.getProgress_percentage());
        p.setCompleted(request.isCompleted());
        if (request.isCompleted() && p.getCompletedDate() == null) {
            p.setCompletedDate(LocalDate.now());
        }
        progressRepository.save(p);

        return toResponse(p);
    }

    public CourseProgressSummaryResponse getCourseProgressSummary(Integer studentId, Integer courseId) {
        Course course = courseRepository.findById(courseId)
            .orElseThrow(() -> new ResourceNotFoundException("Course not found: " + courseId));

        List<Module> modules = moduleRepository.findByCourseIdOrderByModuleIdAsc(courseId);
        int totalLessons = 0;
        int completedLessons = 0;

        for (Module m : modules) {
            List<Lesson> lessons = lessonRepository.findByModuleIdOrderByLessonIdAsc(m.getModuleId());
            totalLessons += lessons.size();
            for (Lesson l : lessons) {
                LessonProgressId id = new LessonProgressId(studentId, l.getLessonId());
                if (progressRepository.findById(id).map(LessonProgress::isCompleted).orElse(false)) {
                    completedLessons++;
                }
            }
        }

        BigDecimal percentage = (totalLessons > 0) ?
            BigDecimal.valueOf((double) completedLessons / totalLessons * 100.0).setScale(2, RoundingMode.HALF_UP)
            : BigDecimal.ZERO;

        return new CourseProgressSummaryResponse(
            course.getCourseId(),
            course.getCourseName(),
            totalLessons,
            completedLessons,
            percentage
        );
    }
}
