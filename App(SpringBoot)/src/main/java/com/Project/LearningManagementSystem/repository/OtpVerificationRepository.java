package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.OtpVerification;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface OtpVerificationRepository extends JpaRepository<OtpVerification, Integer> {
    Optional<OtpVerification> findTopByUidAndPurposeOrderByCreatedAtDesc(String uid, String purpose);
    void deleteByUid(String uid);
}
