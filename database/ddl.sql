CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL UNIQUE,
    first_name TEXT,
    username TEXT,
    type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_log_history (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    update_id INTEGER NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES users (chat_id)
);

CREATE TABLE IF NOT EXISTS message_content (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    audio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES message_log_history (id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 1000),
    value_paid FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES users (chat_id)
);