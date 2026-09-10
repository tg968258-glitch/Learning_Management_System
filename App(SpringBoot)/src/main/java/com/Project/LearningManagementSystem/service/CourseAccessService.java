package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.exception.ForbiddenException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseTeacherRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CourseAccessService {
    private final TeacherRepository teacherRepository;
    private final CourseTeacherRepository courseTeacherRepository;

    public Integer requireAssignedTeacher(String uid, Integer courseId) {
        Teacher teacher = teacherRepository.findByUid(uid)
                .orElseThrow(() -> new ResourceNotFoundException("Teacher profile not found"));
        if (!courseTeacherRepository.existsByIdCourseIdAndIdTeacherId(courseId, teacher.getTeacherId())) {
            throw new ForbiddenException("You can only manage content for courses assigned to you");
        }
        return teacher.getTeacherId();
    }
}
