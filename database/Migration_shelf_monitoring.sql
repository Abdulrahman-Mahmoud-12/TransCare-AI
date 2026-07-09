-- Migration: extend shelf_detections with status + KPI + JSON columns
-- Your retailiq.db is SQLite, so this uses ALTER TABLE ADD COLUMN
-- (SQLite doesn't support adding columns with complex constraints in one
-- statement, so JSON columns are just added as plain columns; SQLAlchemy's
-- JSON type stores them as TEXT under SQLite anyway).

ALTER TABLE shelf_detections ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';
ALTER TABLE shelf_detections ADD COLUMN classes_detected INTEGER DEFAULT 0;
ALTER TABLE shelf_detections ADD COLUMN avg_confidence NUMERIC(5,2);
ALTER TABLE shelf_detections ADD COLUMN processing_time_ms INTEGER;
ALTER TABLE shelf_detections ADD COLUMN detections TEXT;
ALTER TABLE shelf_detections ADD COLUMN category_breakdown TEXT;
ALTER TABLE shelf_detections ADD COLUMN error_message VARCHAR(255);

CREATE INDEX IF NOT EXISTS ix_shelf_detections_status ON shelf_detections(status);

-- Run with: sqlite3 retailiq.db < database/migration_shelf_monitoring.sql
-- Existing rows will get status='pending' by default — you may want to
-- backfill those manually to 'completed' if they already have results:
-- UPDATE shelf_detections SET status='completed' WHERE total_products > 0;