-- deploy/schema.sql
-- Telebots additions to the shared botfarm database.
-- The core tables (bots, documents, document_chunks, conversations, messages)
-- already exist from bot-army. This file adds only what telebots needs on top.
-- Safe to run multiple times (IF NOT EXISTS).

-- Telegram-specific: track chat sessions per bot
CREATE TABLE IF NOT EXISTS telegram_sessions (
    id           SERIAL PRIMARY KEY,
    bot_id       INTEGER REFERENCES bots(id),
    telegram_chat_id BIGINT NOT NULL,
    username     VARCHAR(255),
    first_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    UNIQUE (bot_id, telegram_chat_id)
);

CREATE INDEX IF NOT EXISTS idx_tg_sessions_bot
    ON telegram_sessions(bot_id);
CREATE INDEX IF NOT EXISTS idx_tg_sessions_chat
    ON telegram_sessions(telegram_chat_id);

-- Optional: location shares log (for anglers geolocation feature)
CREATE TABLE IF NOT EXISTS location_shares (
    id           SERIAL PRIMARY KEY,
    bot_id       INTEGER REFERENCES bots(id),
    telegram_chat_id BIGINT,
    latitude     NUMERIC(10, 7),
    longitude    NUMERIC(10, 7),
    shared_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
