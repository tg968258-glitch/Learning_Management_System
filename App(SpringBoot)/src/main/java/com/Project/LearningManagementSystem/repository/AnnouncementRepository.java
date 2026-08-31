package com.Project.LearningManagementSystem.repository;

import com.Project.LearningManagementSystem.entity.Announcement;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AnnouncementRepository extends JpaRepository<Announcement, Integer> {
    List<Announcement> findByCourseIdOrderByCreatedAtDesc(Integer courseId);
}
