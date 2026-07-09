-- Migration: add full_category_distribution + insights columns
-- Run AFTER migration_shelf_monitoring.sql
-- Windows PowerShell: sqlite3 retailiq.db ".read database/migration_shelf_monitoring_insights.sql"
 
ALTER TABLE shelf_detections ADD COLUMN full_category_distribution TEXT;
ALTER TABLE shelf_detections ADD COLUMN insights TEXT;