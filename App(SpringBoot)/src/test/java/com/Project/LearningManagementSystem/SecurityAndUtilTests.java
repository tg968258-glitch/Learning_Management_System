package com.Project.LearningManagementSystem;

import com.Project.LearningManagementSystem.security.JwtUtils;
import com.Project.LearningManagementSystem.util.StringSanitizer;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;
import static org.junit.jupiter.api.Assertions.*;

class SecurityAndUtilTests {

    @Test
    void testJwtGenerateAndValidate() {
        JwtUtils jwtUtils = new JwtUtils();
        ReflectionTestUtils.setField(jwtUtils, "jwtSecret", "your-256-bit-secret-your-256-bit-secret-key-12345");
        ReflectionTestUtils.setField(jwtUtils, "expirationMinutes", 60L);

        String token = jwtUtils.generateToken("USR001", "student");
        assertNotNull(token);
        assertTrue(jwtUtils.isTokenValid(token));
        assertEquals("USR001", jwtUtils.extractUid(token));
        assertEquals("student", jwtUtils.extractRole(token));
    }

    @Test
    void testStringSanitizer() {
        assertEquals("Hello", StringSanitizer.removeSpaces("   Hello   "));
        assertEquals("test", StringSanitizer.toLowerCase("TEST"));
        assertEquals("HELLO", StringSanitizer.toUpperCase("hello"));
        assertEquals("Student", StringSanitizer.capitalizeText("student"));
    }
}
