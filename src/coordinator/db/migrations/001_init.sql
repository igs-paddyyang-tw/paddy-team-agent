-- 001_init.sql: Platform DB schema
CREATE TABLE IF NOT EXISTS agents (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'worker',
    provider    TEXT DEFAULT 'kiro-cli',
    status      TEXT DEFAULT 'idle',
    working_dir TEXT DEFAULT '.',
    model       TEXT DEFAULT 'auto',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS issues (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'pending',
    priority    INTEGER DEFAULT 3,
    assignee    TEXT REFERENCES agents(id),
    blocked_by  TEXT REFERENCES issues(id),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_sessions (
    id          TEXT PRIMARY KEY,
    agent_id    TEXT NOT NULL,
    issue_id    TEXT,
    status      TEXT NOT NULL DEFAULT 'running',
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    total_tokens INTEGER DEFAULT 0,
    cost_usd    REAL DEFAULT 0.0,
    output      TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS cost_records (
    id          TEXT PRIMARY KEY,
    agent_id    TEXT NOT NULL,
    session_id  TEXT,
    issue_id    TEXT,
    model       TEXT NOT NULL,
    input_tokens  INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd    REAL NOT NULL DEFAULT 0.0,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    id          TEXT PRIMARY KEY,
    actor_type  TEXT NOT NULL,
    actor_id    TEXT,
    actor_name  TEXT,
    action      TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    resource_name TEXT,
    details     TEXT DEFAULT '{}',
    timestamp   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS budget_configs (
    workspace_id    TEXT PRIMARY KEY DEFAULT 'default',
    daily_limit_usd REAL DEFAULT 30.0,
    weekly_limit_usd REAL DEFAULT 150.0,
    alert_threshold INTEGER DEFAULT 80
);

CREATE TABLE IF NOT EXISTS session_turns (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL,
    idx         INTEGER NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT DEFAULT '',
    tool_calls  TEXT DEFAULT '[]',
    tokens      INTEGER DEFAULT 0,
    timestamp   TEXT NOT NULL
);
