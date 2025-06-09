-- Rollback for create users table migration

DROP INDEX IF EXISTS ix_users_id;
DROP INDEX IF EXISTS ix_users_username;
DROP INDEX IF EXISTS ix_users_email;
DROP TABLE IF EXISTS users;
