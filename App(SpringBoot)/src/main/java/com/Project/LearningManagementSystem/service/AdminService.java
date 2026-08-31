package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.entity.Teacher;
import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.AssignmentRepository;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.EnrollmentRepository;
import com.Project.LearningManagementSystem.repository.QuizRepository;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.TeacherRepository;
import com.Project.LearningManagementSystem.repository.UserRepository;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AdminService {

    private final UserRepository userRepository;
    private final TeacherRepository teacherRepository;
    private final StudentRepository studentRepository;
    private final CourseRepository courseRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final AssignmentRepository assignmentRepository;
    private final QuizRepository quizRepository;
    private final AuthService authService;
    private final PasswordEncoder passwordEncoder;

    public Map<String, Object> getDashboardData() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("total_users", userRepository.count());
        stats.put("total_students", studentRepository.count());
        stats.put("total_teachers", teacherRepository.count());
        stats.put("total_courses", courseRepository.count());
        stats.put("total_enrollments", enrollmentRepository.count());
        stats.put("total_assignments", assignmentRepository.count());
        stats.put("total_quizzes", quizRepository.count());
        return stats;
    }

    public List<User> getAllUsers(String role, Boolean isActive) {
        if (role != null && !role.isBlank()) {
            return userRepository.findByRole(role);
        }
        if (isActive != null) {
            return userRepository.findByActive(isActive);
        }
        return userRepository.findAll();
    }

    @Transactional
    public User toggleUserActiveStatus(String uid, boolean isActive) {
        User user = userRepository.findById(uid)
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + uid));

        user.setActive(isActive);
        user.setDeactivatedAt(isActive ? null : LocalDateTime.now());
        return userRepository.save(user);
    }

    @Transactional
    public Map<String, Object> createTeacherDirectly(String email, String username, String password,
            String name, String phoneNumber, String specialization,
            String qualification, Integer experience) {
        email = email.trim().toLowerCase();

        if (userRepository.existsByEmail(email)) {
            throw new BadRequestException("User with this email already exists");
        }

        String uid = authService.generateUid();

        User user = new User();
        user.setUid(uid);
        user.setUsername(username.trim());
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(password));
        user.setRole("teacher");
        user.setEmailVerified(true);
        user.setActive(true);
        userRepository.save(user);

        Teacher teacher = new Teacher();
        teacher.setUid(uid);
        teacher.setName(name.trim());
        teacher.setPhoneNumber(phoneNumber);
        teacher.setSpecialization(specialization);
        teacher.setQualification(qualification);
        teacher.setExperience(experience);
        teacherRepository.save(teacher);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Teacher created successfully");
        response.put("uid", user.getUid());
        response.put("username", user.getUsername());
        response.put("email", user.getEmail());
        response.put("role", user.getRole());
        response.put("teacher_id", teacher.getTeacherId());
        return response;
    }
}
