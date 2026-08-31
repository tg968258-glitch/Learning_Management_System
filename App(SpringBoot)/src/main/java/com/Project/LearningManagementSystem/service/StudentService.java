package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.StudentDtos.StudentResponse;
import com.Project.LearningManagementSystem.dto.StudentDtos.StudentUpdateRequest;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class StudentService {

    private final StudentRepository studentRepository;
    private final UserRepository userRepository;

    @Cacheable(value = "studentProfiles", key = "#uid")
    public StudentResponse getStudentProfile(String uid) {
        Student student = studentRepository.findByUid(uid)
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found for UID: " + uid));

        User user = userRepository.findById(uid).orElse(null);

        return new StudentResponse(
            student.getStudentId(),
            student.getUid(),
            null, // roll_number
            student.getName(),
            user != null ? user.getEmail() : null,
            student.getDateOfBirth(),
            student.getGender(),
            student.getPhoneNumber(),
            null // enrollment_date
        );
    }

    @Cacheable(value = "students", key = "'all'")
    public List<Student> getAllStudents() {
        return studentRepository.findAll();
    }

    @Transactional
    @CacheEvict(value = {"studentProfiles", "students"}, allEntries = true)
    public StudentResponse updateStudentProfile(String uid, StudentUpdateRequest request) {
        Student student = studentRepository.findByUid(uid)
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found for UID: " + uid));

        if (request.getName() != null && !request.getName().isBlank()) {
            student.setName(request.getName().trim());
        }
        if (request.getDate_of_birth() != null) {
            student.setDateOfBirth(request.getDate_of_birth());
        }
        if (request.getGender() != null) {
            student.setGender(request.getGender());
        }
        if (request.getPhone_number() != null) {
            student.setPhoneNumber(request.getPhone_number().trim());
        }

        studentRepository.save(student);
        return getStudentProfile(uid);
    }
}
