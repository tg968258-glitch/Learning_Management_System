package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.TeacherInvitation;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TeacherInvitationRepository extends JpaRepository<TeacherInvitation, Integer> {
    Optional<TeacherInvitation> findByTokenHash(String tokenHash);
    Optional<TeacherInvitation> findByEmailAndUsed(String email, boolean used);
    Optional<TeacherInvitation> findByEmail(String email);
}
