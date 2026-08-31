package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.UserSession;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserSessionRepository extends JpaRepository<UserSession, String> {
    List<UserSession> findByUid(String uid);
    Optional<UserSession> findByRefreshTokenHash(String refreshTokenHash);
    Optional<UserSession> findBySessionIdAndUid(String sessionId, String uid);
    void deleteByUid(String uid);
}
