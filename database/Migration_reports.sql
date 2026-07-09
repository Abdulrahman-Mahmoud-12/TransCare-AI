-- database/migrations/migration_reports.sql
-- Creates the `reports` table used to track generated business reports.
-- Naming follows your existing Migration_shelf_monitoring.sql convention.
 
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    date_from DATETIME NOT NULL,
    date_to DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    file_path VARCHAR(500),
    error_message TEXT,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (created_by) REFERENCES users(id)
);