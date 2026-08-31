package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.EnrollmentDtos.EnrollmentResponse;
import com.Project.LearningManagementSystem.entity.Course;
import com.Project.LearningManagementSystem.entity.Enrollment;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.EnrollmentRepository;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import java.time.LocalDate;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class EnrollmentService {

    private final EnrollmentRepository enrollmentRepository;
    private final StudentRepository studentRepository;
    private final CourseRepository courseRepository;

    public EnrollmentResponse toResponse(Enrollment e) {
        String studentName = studentRepository.findById(e.getStudentId()).map(Student::getName).orElse(null);
        String courseName = courseRepository.findById(e.getCourseId()).map(Course::getCourseName).orElse(null);

        return new EnrollmentResponse(
            e.getEnrollmentId(),
            e.getStudentId(),
            e.getCourseId(),
            e.getEnrollmentDate(),
            e.getStatus(),
            studentName,
            courseName
        );
    }

    public List<EnrollmentResponse> getStudentEnrollments(Integer studentId) {
        return enrollmentRepository.findByStudentId(studentId).stream().map(this::toResponse).toList();
    }

    public List<EnrollmentResponse> getCourseEnrollments(Integer courseId) {
        return enrollmentRepository.findByCourseId(courseId).stream().map(this::toResponse).toList();
    }

    @Transactional
    public EnrollmentResponse enrollStudent(Integer studentId, Integer courseId) {
        if (!studentRepository.existsById(studentId)) {
            throw new ResourceNotFoundException("Student not found: " + studentId);
        }
        if (!courseRepository.existsById(courseId)) {
            throw new ResourceNotFoundException("Course not found: " + courseId);
        }
        if (enrollmentRepository.existsByStudentIdAndCourseId(studentId, courseId)) {
            throw new BadRequestException("Student is already enrolled in this course");
        }

        Enrollment enrollment = new Enrollment();
        enrollment.setStudentId(studentId);
        enrollment.setCourseId(courseId);
        enrollment.setEnrollmentDate(LocalDate.now());
        enrollment.setStatus("active");
        enrollmentRepository.save(enrollment);

        return toResponse(enrollment);
    }

    @Transactional
    public EnrollmentResponse updateEnrollmentStatus(Integer enrollmentId, String status) {
        Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
            .orElseThrow(() -> new ResourceNotFoundException("Enrollment not found: " + enrollmentId));

        enrollment.setStatus(status.toLowerCase());
        enrollmentRepository.save(enrollment);
        return toResponse(enrollment);
    }
}
