CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    abstract TEXT,
    url TEXT NOT NULL,
    journal TEXT NOT NULL,
    query_type TEXT NOT NULL,
    publication_date TEXT,
    volume TEXT,
    issue TEXT,
    status TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS update_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    papers_checked INTEGER DEFAULT 0,
    papers_added INTEGER DEFAULT 0,
    papers_updated INTEGER DEFAULT 0,
    log_message TEXT
);

CREATE TABLE IF NOT EXISTS agent_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi TEXT UNIQUE NOT NULL,
    theory_review TEXT,
    theory_score INTEGER,
    grid_review TEXT,
    grid_score INTEGER,
    educational_digest TEXT,
    key_acronyms TEXT,
    curated_at TEXT NOT NULL,
    FOREIGN KEY(doi) REFERENCES papers(doi)
);

CREATE TABLE IF NOT EXISTS triage_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    abstract TEXT,
    url TEXT NOT NULL,
    journal TEXT NOT NULL,
    query_type TEXT NOT NULL,
    publication_date TEXT,
    volume TEXT,
    issue TEXT,
    status TEXT NOT NULL,
    flag_reason TEXT,
    evidence TEXT,
    triage_status TEXT NOT NULL DEFAULT 'pending',
    flagged_at TEXT NOT NULL,
    reviewed_at TEXT
);
