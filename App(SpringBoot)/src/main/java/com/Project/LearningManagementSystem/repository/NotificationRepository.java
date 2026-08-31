package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Notification;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NotificationRepository extends JpaRepository<Notification, Integer> {
    List<Notification> findByUidOrderByCreatedAtDesc(String uid);
    List<Notification> findByUidAndReadOrderByCreatedAtDesc(String uid, boolean read);
}
