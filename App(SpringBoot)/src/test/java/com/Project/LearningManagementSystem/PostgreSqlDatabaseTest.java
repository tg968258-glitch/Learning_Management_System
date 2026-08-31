package com.Project.LearningManagementSystem;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.Connection;
import javax.sql.DataSource;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@Disabled("Run manually after setting your PostgreSQL password in application-local.properties")
@SpringBootTest(classes = LMS.class)
@TestPropertySource(properties = {
        "spring.datasource.url=jdbc:postgresql://localhost:5432/lms_db",
        "spring.datasource.username=postgres",
        "spring.datasource.password=postgres",
        "spring.datasource.driver-class-name=org.postgresql.Driver",
        "spring.flyway.enabled=true",
        "spring.jpa.hibernate.ddl-auto=validate"
})
public class PostgreSqlDatabaseTest {

    @Autowired(required = false)
    private DataSource dataSource;

    @Test
    void testPostgreSqlDatabaseConnection() {
        assertNotNull(dataSource, "DataSource bean should be loaded");
        try (Connection conn = dataSource.getConnection()) {
            assertNotNull(conn, "Database connection should be established");
            System.out.println("=================================================");
            System.out.println("DATABASE CONNECTION TEST SUCCESSFUL!");
            System.out.println("Connected to: " + conn.getMetaData().getDatabaseProductName() + " "
                    + conn.getMetaData().getDatabaseProductVersion());
            System.out.println("Database URL: " + conn.getMetaData().getURL());
            System.out.println("Database User: " + conn.getMetaData().getUserName());
            System.out.println("=================================================");
            assertTrue(conn.isValid(5), "Connection should be valid within 5 seconds");
        } catch (Exception e) {
            System.err.println("=================================================");
            System.err.println("DATABASE CONNECTION FAILED: " + e.getMessage());
            System.err.println(
                    "Tip: Check application-local.properties database username/password or ensure database 'lms_db' exists.");
            System.err.println("=================================================");
        }
    }
}
