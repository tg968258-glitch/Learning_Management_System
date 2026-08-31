package com.Project.LearningManagementSystem;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class LMS {

	public static void main(String[] args) {
		SpringApplication.run(LMS.class, args);
	}

}

