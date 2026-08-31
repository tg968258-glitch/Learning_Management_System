package com.Project.LearningManagementSystem.controller;

import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionCreateRequest;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionResponse;
import com.Project.LearningManagementSystem.dto.CommunicationDtos.DiscussionUpdateRequest;
import com.Project.LearningManagementSystem.security.UserPrincipal;
import com.Project.LearningManagementSystem.service.DiscussionService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
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
@RequestMapping("/discussions")
@Tag(name = "Discussions")
@RequiredArgsConstructor
public class DiscussionController {

    private final DiscussionService discussionService;

    @GetMapping("/course/{course_id}")
    public ResponseEntity<List<DiscussionResponse>> listDiscussions(@PathVariable Integer course_id) {
        return ResponseEntity.ok(discussionService.getDiscussionsByCourse(course_id));
    }

    @PostMapping("/")
    public ResponseEntity<DiscussionResponse> postMessage(
            @Valid @RequestBody DiscussionCreateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(discussionService.createDiscussion(request, currentUser.getUid()));
    }

    @PutMapping("/{discussion_id}")
    public ResponseEntity<DiscussionResponse> editMessage(
            @PathVariable Integer discussion_id,
            @Valid @RequestBody DiscussionUpdateRequest request,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        return ResponseEntity.ok(discussionService.updateDiscussion(discussion_id, request, currentUser.getUid()));
    }

    @DeleteMapping("/{discussion_id}")
    public ResponseEntity<Map<String, String>> removeMessage(
            @PathVariable Integer discussion_id,
            @AuthenticationPrincipal UserPrincipal currentUser) {
        boolean isAdmin = "ADMIN".equalsIgnoreCase(currentUser.getRole());
        discussionService.deleteDiscussion(discussion_id, currentUser.getUid(), isAdmin);
        return ResponseEntity.ok(Map.of("message", "Discussion message deleted successfully"));
    }
}
