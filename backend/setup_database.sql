-- ============================================================
--  setup_database.sql  —  Run this ONCE in PostgreSQL to
--  create the database before starting the Flask server.
--
--  HOW TO RUN THIS:
--  1. Open pgAdmin (installed with PostgreSQL)
--  2. Open the Query Tool
--  3. Paste this entire file and click Run (▶)
--
--  OR use the command line:
--  psql -U postgres -f setup_database.sql
-- ============================================================

-- Create the database (only runs if it doesn't already exist)
-- Note: In PostgreSQL you can't use IF NOT EXISTS with CREATE DATABASE
-- So we check the pg_database system table first
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'its_db'
   ) THEN
      PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE its_db');
   END IF;
END
$$;
