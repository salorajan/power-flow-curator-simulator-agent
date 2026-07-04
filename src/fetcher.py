import requests
import re
from datetime import datetime
import database
import guardrails


# Journal configuration (names and their ISSNs)
JOURNALS = {
    "IEEE Transactions on Power Systems": ["0885-8950", "1558-0679"],
    "IEEE Transactions on Power Delivery": ["0885-8977", "1937-4208"],
    "IEEE Transactions on Smart Grid": ["1949-3053", "2159-8398"]
}

QUERIES = ["power flow", "optimal power flow"]

def clean_abstract(abstract_xml):
    """
    Strips JATS XML tags and cleans up whitespace from abstracts.
    """
    if not abstract_xml:
        return ""
    # Strip HTML/XML tags
    text = re.sub(r'<[^>]+>', ' ', abstract_xml)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    # Strip common leading labels like "Abstract—" or "Abstract"
    text = re.sub(r'^(Abstract|Abstract\s*[-—–]+)\s*', '', text, flags=re.IGNORECASE)
    return text

def parse_date(item):
    """
    Tries to find the most accurate publication date from Crossref metadata.
    """
    for field in ["published-online", "published-print", "created", "issued"]:
        date_parts = item.get(field, {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            parts = date_parts[0]
            # Convert parts to YYYY-MM-DD or YYYY-MM
            parts_str = [f"{p:02d}" if idx > 0 else str(p) for idx, p in enumerate(parts)]
            return "-".join(parts_str)
    return "Unknown Date"

def match_paper_keywords(title, abstract):
    """
    Determines if the paper matches our target topics based on strict local filtering.
    Returns: (matches_opf, matches_pf)
    """
    title_lower = title.lower() if title else ""
    abstract_lower = abstract.lower() if abstract else ""
    
    # 1. Check for Optimal Power Flow
    # Matches: "optimal power flow", "optimal load flow", word boundaries for "opf" or "scopf" or "dopf"
    opf_patterns = [
        r"optimal\s+power\s+flow",
        r"optimal\s+load\s+flow",
        r"\bopf\b",
        r"\bscopf\b",
        r"\bdopf\b"
    ]
    matches_opf = False
    for pat in opf_patterns:
        if re.search(pat, title_lower) or re.search(pat, abstract_lower):
            matches_opf = True
            break
            
    # 2. Check for Power Flow
    # Matches: "power flow", "load flow", "power-flow"
    pf_patterns = [
        r"power\s+flow",
        r"load\s+flow",
        r"power-flow"
    ]
    matches_pf = False
    for pat in pf_patterns:
        if re.search(pat, title_lower) or re.search(pat, abstract_lower):
            matches_pf = True
            break
            
    # Note: Any OPF paper is also a PF paper
    if matches_opf:
        matches_pf = True
        
    return matches_opf, matches_pf

def fetch_and_update(log_id=None):
    """
    Fetches papers from Crossref for IEEE Transactions on Power Systems only.
    Starts search from 2026. If less than 10 matching papers are found, falls back
    to 2025. Filters, performs keyword matching, scans security guardrails, and
    saves/updates them in the database.
    """
    if log_id is None:
        log_id = database.start_update_log()
        
    headers = {
        "User-Agent": "IEEE-Paper-Fetcher/1.0 (mailto:ieee-fetcher@power-app.local)"
    }
    
    papers_checked = 0
    papers_added = 0
    papers_updated = 0
    log_messages = []
    
    journal_name = "IEEE Transactions on Power Systems"
    issns = ["0885-8950", "1558-0679"]
    
    log_messages.append(f"Starting Crossref API fetch for {journal_name} only.")
    
    fetched_papers = {}
    
    def fetch_for_year(year):
        year_papers = {}
        nonlocal papers_checked
        log_messages.append(f"Querying Crossref for year: {year}")
        for query_term in QUERIES:
            log_messages.append(f"  Searching for keyword: '{query_term}' in {year}")
            for issn in issns:
                # Query Crossref with year specific publication bounds
                url = f"https://api.crossref.org/works?filter=issn:{issn},from-pub-date:{year}-01-01,until-pub-date:{year}-12-31&query={query_term}&rows=100"
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        log_messages.append(f"    ISSN {issn} returned status code {response.status_code}")
                        continue
                        
                    data = response.json()
                    items = data.get("message", {}).get("items", [])
                    log_messages.append(f"    ISSN {issn} returned {len(items)} works for {year}.")
                    
                    for item in items:
                        papers_checked += 1
                        doi = item.get("DOI")
                        if not doi:
                            continue
                            
                        title = item.get("title", [""])[0]
                        if not title:
                            continue
                            
                        raw_abstract = item.get("abstract", "")
                        abstract = clean_abstract(raw_abstract)
                        
                        # Apply keyword filters locally
                        matches_opf, matches_pf = match_paper_keywords(title, abstract)
                        if not (matches_opf or matches_pf):
                            continue
                            
                        query_type = "optimal power flow" if matches_opf else "power flow"
                        
                        authors_list = []
                        for auth in item.get("author", []):
                            given = auth.get("given", "")
                            family = auth.get("family", "")
                            authors_list.append(f"{given} {family}".strip())
                        authors = ", ".join(authors_list) if authors_list else "Unknown"
                        
                        link = item.get("URL", f"https://doi.org/{doi}")
                        pub_date = parse_date(item)
                        volume = item.get("volume")
                        issue = item.get("issue")
                        status = "Early Access" if not (volume or issue) else "Published"
                        
                        paper_data = {
                            "doi": doi,
                            "title": title,
                            "authors": authors,
                            "abstract": abstract,
                            "url": link,
                            "journal": journal_name,
                            "query_type": query_type,
                            "publication_date": pub_date,
                            "volume": volume,
                            "issue": issue,
                            "status": status
                        }
                        
                        if doi in year_papers:
                            existing_qt = year_papers[doi]["query_type"]
                            if existing_qt != query_type:
                                year_papers[doi]["query_type"] = "both"
                        else:
                            year_papers[doi] = paper_data
                            
                except Exception as e:
                    log_messages.append(f"    Error querying ISSN {issn} for {year}: {str(e)}")
        return year_papers

    # 1. Fetch for 2026
    papers_2026 = fetch_for_year(2026)
    fetched_papers.update(papers_2026)
    log_messages.append(f"Found {len(papers_2026)} unique matching papers in 2026.")
    
    # 2. Check if count < 10, then fall back to 2025
    if len(fetched_papers) < 10:
        log_messages.append(f"Fewer than 10 papers found for 2026 ({len(fetched_papers)} papers). Going back one year to 2025...")
        papers_2025 = fetch_for_year(2025)
        fetched_papers.update(papers_2025)
        log_messages.append(f"Found {len(papers_2025)} unique matching papers in 2025. Total unique papers now: {len(fetched_papers)}")
    else:
        log_messages.append(f"At least 10 papers found for 2026 ({len(fetched_papers)} papers). Skipping 2025 search.")
        
    # Write fetched papers to database
    log_messages.append(f"Writing {len(fetched_papers)} filtered and matched papers to the database...")
    papers_flagged = 0
    for doi, paper_data in fetched_papers.items():
        try:
            # Run security scan
            is_flagged, flag_reason, evidence = guardrails.scan_paper(paper_data)
            if is_flagged:
                papers_flagged += 1
                log_messages.append(f"  WARNING: DOI {doi} flagged by security guardrail. Reason: {flag_reason}. Evidence: {evidence}")
                database.add_to_triage_queue(paper_data, flag_reason, evidence)
                continue
                
            added, updated = database.add_or_update_paper(paper_data)
            if added:
                papers_added += 1
            if updated:
                papers_updated += 1
        except Exception as e:
            log_messages.append(f"  Error database insertion/triage routing for DOI {doi}: {str(e)}")
            
    summary_message = (
        f"Fetch completed. Checked: {papers_checked} raw works. "
        f"Added: {papers_added} new papers. Flagged for Triage: {papers_flagged} papers. "
        f"Updated: {papers_updated} papers. Total unique papers matched this run: {len(fetched_papers)}."
    )
    log_messages.append(summary_message)
    
    # Save the log
    full_log = "\n".join(log_messages)
    database.update_update_log(log_id, "completed", papers_checked, papers_added, papers_updated, full_log)
    
    return {
        "status": "completed",
        "papers_checked": papers_checked,
        "papers_added": papers_added,
        "papers_flagged": papers_flagged,
        "papers_updated": papers_updated,
        "message": summary_message
    }

