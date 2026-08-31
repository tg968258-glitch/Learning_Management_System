package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.TeacherDtos.TeacherResponse;
import com.Project.LearningManagementSystem.dto.TeacherDtos.TeacherUpdateRequest;
import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class TeacherService {

    private final TeacherRepository teacherRepository;
    private final UserRepository userRepository;

    @Cacheable(value = "teacherProfiles", key = "#uid")
    public TeacherResponse getTeacherProfile(String uid) {
        Teacher teacher = teacherRepository.findByUid(uid)
            .orElseThrow(() -> new ResourceNotFoundException("Teacher profile not found for UID: " + uid));

        User user = userRepository.findById(uid).orElse(null);

        return new TeacherResponse(
            teacher.getTeacherId(),
            teacher.getUid(),
            null, // employee_code
            teacher.getName(),
            user != null ? user.getEmail() : null,
            teacher.getPhoneNumber(),
            null, // department
            teacher.getSpecialization(),
            teacher.getQualification(),
            teacher.getExperience(),
            null // joining_date
        );
    }

    @Cacheable(value = "teachers", key = "'all'")
    public List<Teacher> getAllTeachers() {
        return teacherRepository.findAll();
    }

    @Transactional
    @CacheEvict(value = {"teacherProfiles", "teachers"}, allEntries = true)
    public TeacherResponse updateTeacherProfile(String uid, TeacherUpdateRequest request) {
        Teacher teacher = teacherRepository.findByUid(uid)
            .orElseThrow(() -> new ResourceNotFoundException("Teacher profile not found for UID: " + uid));

        if (request.getName() != null && !request.getName().isBlank()) {
            teacher.setName(request.getName().trim());
        }
        if (request.getPhone_number() != null) {
            teacher.setPhoneNumber(request.getPhone_number().trim());
        }
        if (request.getSpecialization() != null) {
            teacher.setSpecialization(request.getSpecialization());
        }
        if (request.getQualification() != null) {
            teacher.setQualification(request.getQualification());
        }
        if (request.getExperience() != null) {
            teacher.setExperience(request.getExperience());
        }

        teacherRepository.save(teacher);
        return getTeacherProfile(uid);
    }
}
