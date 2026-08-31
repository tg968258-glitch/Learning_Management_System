-- ============================================================
-- V2__add_meeting_link_to_class_sessions.sql
-- Add meeting_link column to class_sessions table
-- ============================================================

ALTER TABLE class_sessions ADD COLUMN IF NOT EXISTS meeting_link VARCHAR(500);
