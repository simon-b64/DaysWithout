CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

INSERT INTO users (id, username, password_hash) VALUES (1, 'default_user', 'NO_LOGIN_INVALID_HASH');

ALTER TABLE days_without ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1 REFERENCES users(id);