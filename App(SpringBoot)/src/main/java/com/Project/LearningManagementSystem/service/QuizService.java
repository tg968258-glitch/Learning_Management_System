package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.QuizDtos.OptionCreateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.OptionResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuestionCreateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuestionResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizAttemptResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizCreateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizDetailResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizSubmitRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.QuizUpdateRequest;
import com.Project.LearningManagementSystem.dto.QuizDtos.StudentAnswerResponse;
import com.Project.LearningManagementSystem.dto.QuizDtos.SubmitAnswerItem;
import com.Project.LearningManagementSystem.entity.QuestionOption;
import com.Project.LearningManagementSystem.entity.Quiz;
import com.Project.LearningManagementSystem.entity.QuizAttempt;
import com.Project.LearningManagementSystem.entity.QuizQuestion;
import com.Project.LearningManagementSystem.entity.StudentAnswer;
import com.Project.LearningManagementSystem.exception.BadRequestException;
import com.Project.LearningManagementSystem.exception.ForbiddenException;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.LessonRepository;
import com.Project.LearningManagementSystem.repository.QuestionOptionRepository;
import com.Project.LearningManagementSystem.repository.QuizAttemptRepository;
import com.Project.LearningManagementSystem.repository.QuizQuestionRepository;
import com.Project.LearningManagementSystem.repository.QuizRepository;
import com.Project.LearningManagementSystem.repository.StudentAnswerRepository;
import java.math.BigDecimal;
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
public class QuizService {

    private final QuizRepository quizRepository;
    private final QuizQuestionRepository questionRepository;
    private final QuestionOptionRepository optionRepository;
    private final QuizAttemptRepository attemptRepository;
    private final StudentAnswerRepository answerRepository;
    private final LessonRepository lessonRepository;

    public QuizResponse toQuizResponse(Quiz q) {
        return new QuizResponse(
                q.getQuizId(),
                q.getLessonId(),
                q.getTitle(),
                q.getDescription(),
                q.getMaxMarks(),
                q.getPassingMarks(),
                q.getDurationMinutes(),
                q.getMaxAttempts(),
                q.isPublished());
    }

    @Cacheable(value = "quizzes", key = "#courseId")
    public List<QuizResponse> getQuizzesByCourse(Integer courseId) {
        return quizRepository.findByCourseId(courseId).stream().map(this::toQuizResponse).toList();
    }

    public QuizDetailResponse getQuizDetail(Integer quizId, boolean isStudent) {
        Quiz q = quizRepository.findById(quizId)
                .orElseThrow(() -> new ResourceNotFoundException("Quiz not found: " + quizId));

        List<QuizQuestion> questions = questionRepository.findByQuizIdOrderByQuestionIdAsc(quizId);
        List<QuestionResponse> qResponses = new ArrayList<>();

        for (QuizQuestion quest : questions) {
            List<QuestionOption> options = optionRepository.findByQuestionId(quest.getQuestionId());
            List<OptionResponse> optResponses = options.stream().map(opt -> new OptionResponse(
                    opt.getOptionId(),
                    opt.getQuestionId(),
                    opt.getOptionText(),
                    isStudent ? null : opt.isCorrect())).toList();

            qResponses.add(new QuestionResponse(
                    quest.getQuestionId(),
                    quest.getQuizId(),
                    quest.getQuestionText(),
                    quest.getQuestionType(),
                    quest.getMarks(),
                    optResponses));
        }

        return new QuizDetailResponse(
                q.getQuizId(),
                q.getLessonId(),
                q.getTitle(),
                q.getDescription(),
                q.getMaxMarks(),
                q.getPassingMarks(),
                q.getDurationMinutes(),
                q.getMaxAttempts(),
                q.isPublished(),
                qResponses);
    }

    @Transactional
    @CacheEvict(value = "quizzes", allEntries = true)
    public QuizResponse createQuiz(QuizCreateRequest request) {
        lessonRepository.findById(request.getLesson_id())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Lesson not found: " + request.getLesson_id()));

        if (request.getPassing_marks().compareTo(request.getMax_marks()) > 0) {
            throw new BadRequestException("Passing marks cannot exceed maximum marks");
        }

        Quiz quiz = new Quiz();
        quiz.setLessonId(request.getLesson_id());
        quiz.setTitle(request.getTitle().trim());
        quiz.setDescription(request.getDescription());
        quiz.setMaxMarks(request.getMax_marks());
        quiz.setPassingMarks(request.getPassing_marks());
        quiz.setDurationMinutes(request.getDuration_minutes());
        quiz.setMaxAttempts(request.getMax_attempts());
        quiz.setPublished(request.is_published());
        quiz.setCreatedAt(LocalDateTime.now());
        quizRepository.save(quiz);

        return toQuizResponse(quiz);
    }

    @Transactional
    @CacheEvict(value = "quizzes", allEntries = true)
    public QuizResponse updateQuiz(Integer quizId, QuizUpdateRequest request) {
        Quiz quiz = quizRepository.findById(quizId)
                .orElseThrow(() -> new ResourceNotFoundException("Quiz not found: " + quizId));

        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            quiz.setTitle(request.getTitle().trim());
        }
        if (request.getDescription() != null) {
            quiz.setDescription(request.getDescription());
        }
        if (request.getMax_marks() != null) {
            quiz.setMaxMarks(request.getMax_marks());
        }
        if (request.getPassing_marks() != null) {
            quiz.setPassingMarks(request.getPassing_marks());
        }
        if (quiz.getPassingMarks().compareTo(quiz.getMaxMarks()) > 0) {
            throw new BadRequestException("Passing marks cannot exceed maximum marks");
        }
        if (request.getDuration_minutes() != null) {
            quiz.setDurationMinutes(request.getDuration_minutes());
        }
        if (request.getMax_attempts() != null) {
            quiz.setMaxAttempts(request.getMax_attempts());
        }
        if (request.getIs_published() != null) {
            quiz.setPublished(request.getIs_published());
        }
        quiz.setUpdatedAt(LocalDateTime.now());
        quizRepository.save(quiz);

        return toQuizResponse(quiz);
    }

    @Transactional
    @CacheEvict(value = "quizzes", allEntries = true)
    public void deleteQuiz(Integer quizId) {
        if (!quizRepository.existsById(quizId)) {
            throw new ResourceNotFoundException("Quiz not found: " + quizId);
        }
        quizRepository.deleteById(quizId);
    }

    @Transactional
    @CacheEvict(value = "quizzes", allEntries = true)
    public QuestionResponse addQuestion(Integer quizId, QuestionCreateRequest request) {
        if (!quizRepository.existsById(quizId)) {
            throw new ResourceNotFoundException("Quiz not found: " + quizId);
        }
        if (request.getOptions() == null || request.getOptions().isEmpty()) {
            throw new BadRequestException("A question must have at least one option");
        }

        QuizQuestion question = new QuizQuestion();
        question.setQuizId(quizId);
        question.setQuestionText(request.getQuestion_text().trim());
        question.setQuestionType(request.getQuestion_type() != null ? request.getQuestion_type() : "mcq");
        question.setMarks(request.getMarks() != null ? request.getMarks() : BigDecimal.ONE);
        questionRepository.save(question);

        List<OptionResponse> optResponses = new ArrayList<>();
        for (OptionCreateRequest optReq : request.getOptions()) {
            QuestionOption opt = new QuestionOption();
            opt.setQuestionId(question.getQuestionId());
            opt.setOptionText(optReq.getOption_text().trim());
            opt.setCorrect(optReq.is_correct());
            optionRepository.save(opt);
            optResponses.add(
                    new OptionResponse(opt.getOptionId(), opt.getQuestionId(), opt.getOptionText(), opt.isCorrect()));
        }

        return new QuestionResponse(
                question.getQuestionId(),
                question.getQuizId(),
                question.getQuestionText(),
                question.getQuestionType(),
                question.getMarks(),
                optResponses);
    }

    @Transactional
    public QuizAttemptResponse startQuizAttempt(Integer quizId, Integer studentId) {
        Quiz quiz = quizRepository.findById(quizId)
                .orElseThrow(() -> new ResourceNotFoundException("Quiz not found: " + quizId));

        if (!quiz.isPublished()) {
            throw new BadRequestException("Quiz is not published yet");
        }

        List<QuizAttempt> attempts = attemptRepository.findByQuizIdAndStudentId(quizId, studentId);
        if (attempts.size() >= quiz.getMaxAttempts()) {
            throw new BadRequestException(
                    "Maximum attempt limit (" + quiz.getMaxAttempts() + ") reached for this quiz");
        }

        int attemptNumber = attempts.size() + 1;
        QuizAttempt attempt = new QuizAttempt();
        attempt.setQuizId(quizId);
        attempt.setStudentId(studentId);
        attempt.setAttemptNumber(attemptNumber);
        attempt.setStartedAt(LocalDateTime.now());
        attempt.setStatus("in_progress");
        attemptRepository.save(attempt);

        return toAttemptResponse(attempt);
    }

    @Transactional
    public QuizAttemptResponse submitQuizAttempt(Integer attemptId, Integer studentId, QuizSubmitRequest request) {
        QuizAttempt attempt = attemptRepository.findById(attemptId)
                .orElseThrow(() -> new ResourceNotFoundException("Quiz attempt not found: " + attemptId));

        if (!attempt.getStudentId().equals(studentId)) {
            throw new ForbiddenException("You can only submit your own quiz attempt");
        }
        if (!"in_progress".equals(attempt.getStatus())) {
            throw new BadRequestException("This quiz attempt has already been submitted");
        }

        Quiz quiz = quizRepository.findById(attempt.getQuizId())
                .orElseThrow(() -> new ResourceNotFoundException("Quiz not found"));

        BigDecimal totalScore = BigDecimal.ZERO;
        List<StudentAnswerResponse> answerResponses = new ArrayList<>();

        for (SubmitAnswerItem item : request.getAnswers()) {
            QuizQuestion question = questionRepository.findById(item.getQuestion_id()).orElse(null);
            if (question == null)
                continue;

            BigDecimal marksAwarded = BigDecimal.ZERO;
            if (item.getSelected_option_id() != null) {
                QuestionOption opt = optionRepository.findById(item.getSelected_option_id()).orElse(null);
                if (opt != null && opt.isCorrect() && opt.getQuestionId().equals(question.getQuestionId())) {
                    marksAwarded = question.getMarks();
                }
            }

            totalScore = totalScore.add(marksAwarded);

            StudentAnswer answer = new StudentAnswer();
            answer.setAttemptId(attemptId);
            answer.setQuestionId(question.getQuestionId());
            answer.setSelectedOptionId(item.getSelected_option_id());
            answer.setMarksAwarded(marksAwarded);
            answerRepository.save(answer);

            answerResponses.add(new StudentAnswerResponse(
                    answer.getAnswerId(), answer.getAttemptId(), answer.getQuestionId(), answer.getSelectedOptionId(),
                    answer.getMarksAwarded()));
        }

        boolean passed = totalScore.compareTo(quiz.getPassingMarks()) >= 0;
        attempt.setSubmittedAt(LocalDateTime.now());
        attempt.setMarks(totalScore);
        attempt.setStatus("completed");
        attempt.setPassed(passed);
        attemptRepository.save(attempt);

        QuizAttemptResponse resp = toAttemptResponse(attempt);
        resp.setAnswers(answerResponses);
        return resp;
    }

    public List<QuizAttemptResponse> getStudentAttempts(Integer quizId, Integer studentId) {
        return attemptRepository.findByQuizIdAndStudentId(quizId, studentId).stream().map(this::toAttemptResponse)
                .toList();
    }

    public QuizAttemptResponse toAttemptResponse(QuizAttempt a) {
        List<StudentAnswerResponse> answers = answerRepository.findByAttemptId(a.getAttemptId()).stream()
                .map(ans -> new StudentAnswerResponse(
                        ans.getAnswerId(), ans.getAttemptId(), ans.getQuestionId(), ans.getSelectedOptionId(),
                        ans.getMarksAwarded()))
                .toList();

        return new QuizAttemptResponse(
                a.getAttemptId(),
                a.getQuizId(),
                a.getStudentId(),
                a.getAttemptNumber(),
                a.getStartedAt(),
                a.getSubmittedAt(),
                a.getMarks(),
                a.getStatus(),
                a.getPassed(),
                answers);
    }
}
