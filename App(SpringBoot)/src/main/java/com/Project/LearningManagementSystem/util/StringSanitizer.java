package com.Project.LearningManagementSystem.util;

public class StringSanitizer {

    public static String removeSpaces(String text) {
        return text == null ? "" : text.trim();
    }

    public static String toLowerCase(String text) {
        return text == null ? "" : text.toLowerCase();
    }

    public static String toUpperCase(String text) {
        return text == null ? "" : text.toUpperCase();
    }

    public static String capitalizeText(String text) {
        if (text == null || text.isEmpty()) return "";
        return text.substring(0, 1).toUpperCase() + text.substring(1).toLowerCase();
    }
}
