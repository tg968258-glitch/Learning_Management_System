package com.example.demo.configuration;

import com.example.demo.service.EmployeeService;
import org.modelmapper.ModelMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EmployeeConfig {

    @Bean
    public EmployeeService employeeService() {
        return new EmployeeService();
    }

    @Bean
    public ModelMapper modelMapper() {
        return new ModelMapper();
    }
}