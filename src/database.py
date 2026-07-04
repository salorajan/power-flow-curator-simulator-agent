import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "papers.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create papers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doi TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        authors TEXT NOT NULL,
        abstract TEXT,
        url TEXT NOT NULL,
        journal TEXT NOT NULL,
        query_type TEXT NOT NULL, -- 'power flow', 'optimal power flow', or 'both'
        publication_date TEXT,     -- YYYY-MM-DD or YYYY-MM
        volume TEXT,
        issue TEXT,
        status TEXT NOT NULL,      -- 'Early Access' or 'Published'
        fetched_at TEXT NOT NULL
    )
    """)
    
    # Create search indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers(doi)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_journal ON papers(journal)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_query_type ON papers(query_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status)")
    
    # Create a table to track update logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS update_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT NOT NULL,      -- 'running', 'completed', 'failed'
        papers_checked INTEGER DEFAULT 0,
        papers_added INTEGER DEFAULT 0,
        papers_updated INTEGER DEFAULT 0,
        log_message TEXT
    )
    """)
    
    # Create agent_reviews table to store multi-agent evaluations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doi TEXT UNIQUE NOT NULL,
        theory_review TEXT,
        theory_score INTEGER,
        grid_review TEXT,
        grid_score INTEGER,
        educational_digest TEXT,
        key_acronyms TEXT,         -- JSON string
        curated_at TEXT NOT NULL,
        FOREIGN KEY(doi) REFERENCES papers(doi)
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_reviews_doi ON agent_reviews(doi)")
    
    # Create triage_queue table for HITL review of flagged items
    cursor.execute("""
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
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_triage_queue_doi ON triage_queue(doi)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_triage_queue_status ON triage_queue(triage_status)")
    
    conn.commit()
    conn.close()


def add_or_update_paper(paper_data):
    """
    Inserts a paper or updates it if it was previously 'Early Access' 
    and now has volume/issue (indicating final publication).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    doi = paper_data['doi']
    now_str = datetime.now().isoformat()
    
    # Check if paper already exists
    cursor.execute("SELECT id, status, volume, issue FROM papers WHERE doi = ?", (doi,))
    existing = cursor.fetchone()
    
    added = False
    updated = False
    
    if existing is None:
        # Insert new paper
        cursor.execute("""
        INSERT INTO papers (
            doi, title, authors, abstract, url, journal, query_type, 
            publication_date, volume, issue, status, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doi,
            paper_data['title'],
            paper_data['authors'],
            paper_data['abstract'],
            paper_data['url'],
            paper_data['journal'],
            paper_data['query_type'],
            paper_data['publication_date'],
            paper_data.get('volume'),
            paper_data.get('issue'),
            paper_data['status'],
            now_str
        ))
        added = True
    else:
        # Paper exists. Check if we should update it.
        # If the existing status is 'Early Access' and we now have volume/issue info, update it.
        existing_status = existing['status']
        new_status = paper_data['status']
        
        # We also merge query types if a paper matches both in different runs
        existing_id = existing['id']
        cursor.execute("SELECT query_type FROM papers WHERE id = ?", (existing_id,))
        existing_query_type = cursor.fetchone()['query_type']
        
        new_query_type = paper_data['query_type']
        merged_query_type = existing_query_type
        if existing_query_type != new_query_type:
            merged_query_type = "both"
            
        if existing_status == "Early Access" and new_status == "Published":
            cursor.execute("""
            UPDATE papers SET 
                volume = ?,
                issue = ?,
                status = ?,
                publication_date = ?,
                query_type = ?,
                fetched_at = ?
            WHERE id = ?
            """, (
                paper_data.get('volume'),
                paper_data.get('issue'),
                "Published",
                paper_data['publication_date'],
                merged_query_type,
                now_str,
                existing_id
            ))
            updated = True
        elif existing_query_type != merged_query_type:
            # Update query type if it has expanded
            cursor.execute("UPDATE papers SET query_type = ? WHERE id = ?", (merged_query_type, existing_id))
            updated = True
            
    conn.commit()
    conn.close()
    return added, updated

def get_papers(filters=None, search_query=None, limit=100, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM papers WHERE 1=1"
    params = []
    
    if filters:
        if filters.get('journal'):
            query += " AND journal = ?"
            params.append(filters['journal'])
        if filters.get('query_type'):
            if filters['query_type'] == 'both':
                query += " AND query_type = 'both'"
            elif filters['query_type'] in ['power flow', 'optimal power flow']:
                query += " AND (query_type = ? OR query_type = 'both')"
                params.append(filters['query_type'])
        if filters.get('status'):
            query += " AND status = ?"
            params.append(filters['status'])
            
    if search_query:
        query += " AND (title LIKE ? OR authors LIKE ? OR abstract LIKE ?)"
        like_pattern = f"%{search_query}%"
        params.extend([like_pattern, like_pattern, like_pattern])
        
    query += " ORDER BY publication_date DESC, fetched_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Get total count for pagination
    count_query = "SELECT COUNT(*) FROM papers WHERE 1=1"
    count_params = []
    if filters:
        if filters.get('journal'):
            count_query += " AND journal = ?"
            count_params.append(filters['journal'])
        if filters.get('query_type'):
            if filters['query_type'] == 'both':
                count_query += " AND query_type = 'both'"
            elif filters['query_type'] in ['power flow', 'optimal power flow']:
                count_query += " AND (query_type = ? OR query_type = 'both')"
                count_params.append(filters['query_type'])
        if filters.get('status'):
            count_query += " AND status = ?"
            count_params.append(filters['status'])
            
    if search_query:
        count_query += " AND (title LIKE ? OR authors LIKE ? OR abstract LIKE ?)"
        count_like_pattern = f"%{search_query}%"
        count_params.extend([count_like_pattern, count_like_pattern, count_like_pattern])
        
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    return [dict(row) for row in rows], total_count

def get_paper_by_id(paper_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total papers
    cursor.execute("SELECT COUNT(*) FROM papers")
    stats['total'] = cursor.fetchone()[0]
    
    # Early Access papers
    cursor.execute("SELECT COUNT(*) FROM papers WHERE status = 'Early Access'")
    stats['early_access'] = cursor.fetchone()[0]
    
    # Published papers
    cursor.execute("SELECT COUNT(*) FROM papers WHERE status = 'Published'")
    stats['published'] = cursor.fetchone()[0]
    
    # Power Flow papers (matches 'power flow' or 'both')
    cursor.execute("SELECT COUNT(*) FROM papers WHERE query_type = 'power flow' OR query_type = 'both'")
    stats['power_flow'] = cursor.fetchone()[0]
    
    # Optimal Power Flow papers (matches 'optimal power flow' or 'both')
    cursor.execute("SELECT COUNT(*) FROM papers WHERE query_type = 'optimal power flow' OR query_type = 'both'")
    stats['optimal_power_flow'] = cursor.fetchone()[0]
    
    # Journal breakdowns
    cursor.execute("SELECT journal, COUNT(*) as count FROM papers GROUP BY journal")
    stats['journals'] = {row['journal']: row['count'] for row in cursor.fetchall()}
    
    # Last update log
    cursor.execute("SELECT * FROM update_logs ORDER BY id DESC LIMIT 1")
    last_log = cursor.fetchone()
    stats['last_update'] = dict(last_log) if last_log else None
    
    conn.close()
    return stats

def start_update_log():
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    
    cursor.execute("""
    INSERT INTO update_logs (started_at, status, log_message)
    VALUES (?, 'running', 'Update started.')
    """, (now_str,))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def update_update_log(log_id, status, papers_checked, papers_added, papers_updated, log_message):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    
    cursor.execute("""
    UPDATE update_logs SET
        completed_at = ?,
        status = ?,
        papers_checked = ?,
        papers_added = ?,
        papers_updated = ?,
        log_message = ?
    WHERE id = ?
    """, (now_str, status, papers_checked, papers_added, papers_updated, log_message, log_id))
    
    conn.commit()
    conn.close()

def add_to_triage_queue(paper_data, flag_reason, evidence):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    doi = paper_data['doi']
    now_str = datetime.now().isoformat()
    
    # Check if paper is already in triage
    cursor.execute("SELECT id FROM triage_queue WHERE doi = ?", (doi,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False
        
    cursor.execute("""
    INSERT INTO triage_queue (
        doi, title, authors, abstract, url, journal, query_type, 
        publication_date, volume, issue, status, flag_reason, evidence, flagged_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doi,
        paper_data['title'],
        paper_data['authors'],
        paper_data['abstract'],
        paper_data['url'],
        paper_data['journal'],
        paper_data['query_type'],
        paper_data.get('publication_date'),
        paper_data.get('volume'),
        paper_data.get('issue'),
        paper_data['status'],
        flag_reason,
        evidence,
        now_str
    ))
    
    conn.commit()
    conn.close()
    return True

def get_triage_queue(status='pending', limit=50, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM triage_queue 
    WHERE triage_status = ? 
    ORDER BY flagged_at DESC 
    LIMIT ? OFFSET ?
    """, (status, limit, offset))
    rows = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM triage_queue WHERE triage_status = ?", (status,))
    total = cursor.fetchone()[0]
    
    conn.close()
    return [dict(row) for row in rows], total

def get_triage_paper_by_id(triage_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_queue WHERE id = ?", (triage_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def approve_triage_paper(triage_id):
    """
    Approves a paper in the triage queue and moves it to the main papers table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM triage_queue WHERE id = ?", (triage_id,))
    row = cursor.fetchone()
    if not row or row['triage_status'] != 'pending':
        conn.close()
        return False
        
    paper_data = dict(row)
    now_str = datetime.now().isoformat()
    
    # 1. Update triage queue status
    cursor.execute("""
    UPDATE triage_queue 
    SET triage_status = 'approved', reviewed_at = ? 
    WHERE id = ?
    """, (now_str, triage_id))
    
    # 2. Insert into papers
    # We check if it already exists in papers (unlikely but safe)
    cursor.execute("SELECT id FROM papers WHERE doi = ?", (paper_data['doi'],))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute("""
        INSERT INTO papers (
            doi, title, authors, abstract, url, journal, query_type, 
            publication_date, volume, issue, status, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_data['doi'],
            paper_data['title'],
            paper_data['authors'],
            paper_data['abstract'],
            paper_data['url'],
            paper_data['journal'],
            paper_data['query_type'],
            paper_data['publication_date'],
            paper_data.get('volume'),
            paper_data.get('issue'),
            paper_data['status'],
            now_str
        ))
        
    conn.commit()
    conn.close()
    return True

def reject_triage_paper(triage_id):
    """
    Rejects a paper in the triage queue.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, triage_status FROM triage_queue WHERE id = ?", (triage_id,))
    row = cursor.fetchone()
    if not row or row['triage_status'] != 'pending':
        conn.close()
        return False
        
    now_str = datetime.now().isoformat()
    cursor.execute("""
    UPDATE triage_queue 
    SET triage_status = 'rejected', reviewed_at = ? 
    WHERE id = ?
    """, (now_str, triage_id))
    
    conn.commit()
    conn.close()
    return True

def add_or_update_agent_review(review_data):
    """
    Saves or updates a multi-agent review summary.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    doi = review_data['doi']
    now_str = datetime.now().isoformat()
    
    # Check if review already exists
    cursor.execute("SELECT id FROM agent_reviews WHERE doi = ?", (doi,))
    existing = cursor.fetchone()
    
    if existing is None:
        cursor.execute("""
        INSERT INTO agent_reviews (
            doi, theory_review, theory_score, grid_review, grid_score, 
            educational_digest, key_acronyms, curated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doi,
            review_data['theory_review'],
            review_data['theory_score'],
            review_data['grid_review'],
            review_data['grid_score'],
            review_data['educational_digest'],
            review_data['key_acronyms'],
            now_str
        ))
    else:
        cursor.execute("""
        UPDATE agent_reviews SET
            theory_review = ?,
            theory_score = ?,
            grid_review = ?,
            grid_score = ?,
            educational_digest = ?,
            key_acronyms = ?,
            curated_at = ?
        WHERE doi = ?
        """, (
            review_data['theory_review'],
            review_data['theory_score'],
            review_data['grid_review'],
            review_data['grid_score'],
            review_data['educational_digest'],
            review_data['key_acronyms'],
            now_str,
            doi
        ))
        
    conn.commit()
    conn.close()
    return True

def get_agent_review(doi):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_reviews WHERE doi = ?", (doi,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

