package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.QuizDtos.QuestionCreateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuestionResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizAttemptResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizCreateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizDetailResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizSubmitRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizUpdateRequest;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.QuizService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/quizzes")
@Tag(name = "Quizzes")
@RequiredArgsConstructor
public class QuizController {

    private final QuizService quizService;
    private final StudentRepository studentRepository;

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<QuizResponse>> listQuizzes(@PathVariable Integer course_id) {
        return ResponseEntity.ok(quizService.getQuizzesByCourse(course_id));
    }

    @GetMapping("/{quiz_id}")
    public ResponseEntity<QuizDetailResponse> getQuiz(
        @PathVariable Integer quiz_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        boolean isStudent = currentUser != null && "STUDENT".equalsIgnoreCase(currentUser.getRole());
        return ResponseEntity.ok(quizService.getQuizDetail(quiz_id, isStudent));
    }

    @PostMapping("/")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<QuizResponse> createQuiz(@Valid @RequestBody QuizCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(quizService.createQuiz(request));
    }

    @PutMapping("/{quiz_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<QuizResponse> updateQuiz(
        @PathVariable Integer quiz_id,
        @Valid @RequestBody QuizUpdateRequest request
    ) {
        return ResponseEntity.ok(quizService.updateQuiz(quiz_id, request));
    }

    @DeleteMapping("/{quiz_id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<Map<String, String>> deleteQuiz(@PathVariable Integer quiz_id) {
        quizService.deleteQuiz(quiz_id);
        return ResponseEntity.ok(Map.of("message", "Quiz deleted successfully"));
    }

    @PostMapping("/{quiz_id}/questions")
    @PreAuthorize("hasAnyRole('ADMIN', 'TEACHER')")
    public ResponseEntity<QuestionResponse> addQuestion(
        @PathVariable Integer quiz_id,
        @Valid @RequestBody QuestionCreateRequest request
    ) {
        return ResponseEntity.status(HttpStatus.CREATED).body(quizService.addQuestion(quiz_id, request));
    }

    @PostMapping("/{quiz_id}/start")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<QuizAttemptResponse> startAttempt(
        @PathVariable Integer quiz_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(quizService.startQuizAttempt(quiz_id, student.getStudentId()));
    }

    @PostMapping("/attempts/{attempt_id}/submit")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<QuizAttemptResponse> submitAttempt(
        @PathVariable Integer attempt_id,
        @Valid @RequestBody QuizSubmitRequest request,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(quizService.submitQuizAttempt(attempt_id, student.getStudentId(), request));
    }

    @GetMapping("/{quiz_id}/my-attempts")
    @PreAuthorize("hasRole('STUDENT')")
    public ResponseEntity<List<QuizAttemptResponse>> getMyAttempts(
        @PathVariable Integer quiz_id,
        @AuthenticationPrincipal UserPrincipal currentUser
    ) {
        Student student = studentRepository.findByUid(currentUser.getUid())
            .orElseThrow(() -> new ResourceNotFoundException("Student profile not found"));
        return ResponseEntity.ok(quizService.getStudentAttempts(quiz_id, student.getStudentId()));
    }
}
