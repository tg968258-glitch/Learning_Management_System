package com.Project.LearningManagementSystem.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "modules")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class Module {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "module_id")
    private Integer moduleId;

    @Column(name = "course_id", nullable = false)
    private Integer courseId;

    @Column(name = "is_published", nullable = false)
    private boolean published = false;

    @Column(name = "published_by", length = 10)
    private String publishedBy;

    @Column(name = "module_name", length = 150, nullable = false)
    private String moduleName;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;
}
