CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    created_at TIMESTAMP,
    is_admin BOOLEAN
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    topic TEXT UNIQUE
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
    message TEXT,
    date TIMESTAMP
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics (id) ON DELETE CASCADE,
    message_id INTEGER REFERENCES messages (id) ON DELETE CASCADE,
    title TEXT
);

CREATE TABLE subthreads (
    id SERIAL PRIMARY KEY,
    parent_msg_id INTEGER REFERENCES messages (id) ON DELETE CASCADE,
    child_msg_id INTEGER REFERENCES messages (id) ON DELETE CASCADE
);

CREATE TABLE pinned_threads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
    thread_id INTEGER REFERENCES threads (id) ON DELETE CASCADE
);