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
@Table(name = "teachers")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor
public class Teacher {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "teacher_id")
    private Integer teacherId;

    @Column(name = "uid", length = 10, nullable = false, unique = true)
    private String uid;

    @Column(name = "name", length = 100, nullable = false)
    private String name;

    @Column(name = "phone_number", length = 15)
    private String phoneNumber;

    @Column(name = "specialization", length = 100)
    private String specialization;

    @Column(name = "qualification", length = 150)
    private String qualification;

    @Column(name = "experience")
    private Integer experience;
}
