package com.Project.LearningManagementSystem.service;

import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentCreateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentDetailResponse;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentResponse;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.AssignmentUpdateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionCreateRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionGradeRequest;
import com.Project.LearningManagementSystem.dto.AssignmentDtos.SubmissionResponse;
import com.Project.LearningManagementSystem.entity.Assignment;
import com.Project.LearningManagementSystem.entity.Student;
import com.Project.LearningManagementSystem.entity.Submission;
import com.Project.LearningManagementSystem.exception.ResourceNotFoundException;
import com.Project.LearningManagementSystem.repository.AssignmentRepository;
import com.Project.LearningManagementSystem.repository.CourseRepository;
import com.Project.LearningManagementSystem.repository.StudentRepository;
import com.Project.LearningManagementSystem.repository.SubmissionRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AssignmentService {

        private final AssignmentRepository assignmentRepository;
        private final SubmissionRepository submissionRepository;
        private final StudentRepository studentRepository;
        private final CourseRepository courseRepository;

        public SubmissionResponse toSubmissionResponse(
                        Submission submission) {

                String studentName = studentRepository
                                .findById(submission.getStudentId())
                                .map(Student::getName)
                                .orElse(null);

                return new SubmissionResponse(
                                submission.getSubmissionId(),
                                submission.getAssignmentId(),
                                submission.getStudentId(),
                                submission.getSubmissionDate(),
                                submission.getSubmissionText(),
                                submission.getSubmissionFile(),
                                submission.getStatus(),
                                submission.getMarks(),
                                submission.getGradedBy(),
                                submission.getFeedback(),
                                studentName);
        }

        public AssignmentResponse toAssignmentResponse(
                        Assignment assignment) {

                return new AssignmentResponse(
                                assignment.getAssignmentId(),
                                assignment.getCourseId(),
                                assignment.getModuleId(),
                                assignment.getTitle(),
                                assignment.getDescription(),
                                assignment.getDueDate(),
                                assignment.getMaxMarks(),
                                assignment.getPassingMarks());
        }

        public List<AssignmentResponse> getAssignmentsByCourse(
                        Integer courseId) {

                return assignmentRepository
                                .findByCourseId(courseId)
                                .stream()
                                .map(this::toAssignmentResponse)
                                .toList();
        }

        public AssignmentDetailResponse getAssignmentDetail(
                        Integer assignmentId) {

                Assignment assignment = assignmentRepository
                                .findById(assignmentId)
                                .orElseThrow(
                                                () -> new ResourceNotFoundException(
                                                                "Assignment not found: " + assignmentId));

                List<SubmissionResponse> submissions = submissionRepository
                                .findByAssignmentId(assignmentId)
                                .stream()
                                .map(this::toSubmissionResponse)
                                .toList();

                return new AssignmentDetailResponse(
                                assignment.getAssignmentId(),
                                assignment.getCourseId(),
                                assignment.getModuleId(),
                                assignment.getTitle(),
                                assignment.getDescription(),
                                assignment.getDueDate(),
                                assignment.getMaxMarks(),
                                assignment.getPassingMarks(),
                                submissions);
        }

        @Transactional
        public AssignmentResponse createAssignment(
                        AssignmentCreateRequest request,
                        String createdByUid) {

                if (!courseRepository.existsById(request.getCourse_id())) {
                        throw new ResourceNotFoundException(
                                        "Course not found: "
                                                        + request.getCourse_id());
                }

                Assignment assignment = new Assignment();

                assignment.setCourseId(request.getCourse_id());
                assignment.setModuleId(request.getModule_id());
                assignment.setTitle(request.getTitle().trim());
                assignment.setDescription(request.getDescription());
                assignment.setDueDate(request.getDue_date());
                assignment.setMaxMarks(request.getMax_marks());
                assignment.setPassingMarks(
                                request.getPassing_marks());
                assignment.setCreatedBy(createdByUid);
                assignment.setCreatedAt(LocalDateTime.now());

                assignmentRepository.save(assignment);

                return toAssignmentResponse(assignment);
        }

        @Transactional
        public AssignmentResponse updateAssignment(
                        Integer assignmentId,
                        AssignmentUpdateRequest request) {

                Assignment assignment = assignmentRepository
                                .findById(assignmentId)
                                .orElseThrow(
                                                () -> new ResourceNotFoundException(
                                                                "Assignment not found: " + assignmentId));

                if (request.getTitle() != null &&
                                !request.getTitle().isBlank()) {
                        assignment.setTitle(
                                        request.getTitle().trim());
                }

                if (request.getDescription() != null) {
                        assignment.setDescription(
                                        request.getDescription());
                }

                if (request.getDue_date() != null) {
                        assignment.setDueDate(
                                        request.getDue_date());
                }

                if (request.getMax_marks() != null) {
                        assignment.setMaxMarks(
                                        request.getMax_marks());
                }

                if (request.getPassing_marks() != null) {
                        assignment.setPassingMarks(
                                        request.getPassing_marks());
                }

                assignment.setUpdatedAt(LocalDateTime.now());

                assignmentRepository.save(assignment);

                return toAssignmentResponse(assignment);
        }

        @Transactional
        public void deleteAssignment(Integer assignmentId) {

                if (!assignmentRepository.existsById(assignmentId)) {
                        throw new ResourceNotFoundException(
                                        "Assignment not found: " + assignmentId);
                }

                assignmentRepository.deleteById(assignmentId);
        }

        @Transactional
        public SubmissionResponse submitAssignment(
                        Integer assignmentId,
                        Integer studentId,
                        SubmissionCreateRequest request) {

                assignmentRepository
                                .findById(assignmentId)
                                .orElseThrow(
                                                () -> new ResourceNotFoundException(
                                                                "Assignment not found: " + assignmentId));

                Submission submission = submissionRepository
                                .findByAssignmentIdAndStudentId(
                                                assignmentId,
                                                studentId)
                                .orElse(new Submission());

                submission.setAssignmentId(assignmentId);
                submission.setStudentId(studentId);
                submission.setSubmissionDate(
                                LocalDateTime.now());
                submission.setSubmissionText(
                                request.getSubmission_text());
                submission.setSubmissionFile(
                                request.getSubmission_file());
                submission.setStatus("submitted");

                submissionRepository.save(submission);

                return toSubmissionResponse(submission);
        }

        @Transactional
        public SubmissionResponse gradeSubmission(
                        Integer assignmentId,
                        Integer studentId,
                        Integer teacherId,
                        SubmissionGradeRequest request) {

                Submission submission = submissionRepository
                                .findByAssignmentIdAndStudentId(
                                                assignmentId,
                                                studentId)
                                .orElseThrow(
                                                () -> new ResourceNotFoundException(
                                                                "Submission not found for assignment "
                                                                                + assignmentId
                                                                                + " and student "
                                                                                + studentId));

                submission.setMarks(request.getMarks());
                submission.setFeedback(request.getFeedback());
                submission.setGradedBy(teacherId);
                submission.setStatus("graded");
                submission.setUpdatedAt(LocalDateTime.now());

                submissionRepository.save(submission);

                return toSubmissionResponse(submission);
        }
}