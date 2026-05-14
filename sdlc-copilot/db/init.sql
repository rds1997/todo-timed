-- Bootstrap script for local Postgres. The schema is owned by EF Core migrations
-- (run automatically by the API on startup). This file only ensures the role
-- and database exist; safe to run on an empty cluster.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sdlc') THEN
        CREATE ROLE sdlc LOGIN PASSWORD 'sdlc';
    END IF;
END
$$;

CREATE DATABASE sdlc_copilot OWNER sdlc;
GRANT ALL PRIVILEGES ON DATABASE sdlc_copilot TO sdlc;
