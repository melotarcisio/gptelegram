CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_log_history (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    update_id INTEGER NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_content (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    audio TEXT
);