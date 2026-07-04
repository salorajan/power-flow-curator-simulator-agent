import database
import fetcher
import agents_curator
import guardrails
import requests
import json

# Setup database
database.init_db()

journal_name = "IEEE Transactions on Power Systems"
issns = ["0885-8950", "1558-0679"]
queries = ["power flow", "optimal power flow"]
headers = {
    "User-Agent": "IEEE-Paper-Fetcher/1.0 (mailto:ieee-fetcher@power-app.local)"
}

print("Fetching publications from Crossref for the year 2025...")
fetched_papers = {}
papers_checked = 0

for query_term in queries:
    print(f"Searching keyword: '{query_term}' in 2025...")
    for issn in issns:
        url = f"https://api.crossref.org/works?filter=issn:{issn},from-pub-date:2025-01-01,until-pub-date:2025-12-31&query={query_term}&rows=100"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                items = response.json().get("message", {}).get("items", [])
                print(f"  ISSN {issn} returned {len(items)} works.")
                for item in items:
                    papers_checked += 1
                    doi = item.get("DOI")
                    if not doi:
                        continue
                    title = item.get("title", [""])[0]
                    if not title:
                        continue
                    abstract = fetcher.clean_abstract(item.get("abstract", ""))
                    matches_opf, matches_pf = fetcher.match_paper_keywords(title, abstract)
                    if not (matches_opf or matches_pf):
                        continue
                    
                    query_type = "optimal power flow" if matches_opf else "power flow"
                    authors_list = [f"{auth.get('given', '')} {auth.get('family', '')}".strip() for auth in item.get("author", [])]
                    authors = ", ".join(authors_list) if authors_list else "Unknown"
                    link = item.get("URL", f"https://doi.org/{doi}")
                    pub_date = fetcher.parse_date(item)
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
                    if doi in fetched_papers:
                        if fetched_papers[doi]["query_type"] != query_type:
                            fetched_papers[doi]["query_type"] = "both"
                    else:
                        fetched_papers[doi] = paper_data
        except Exception as e:
            print(f"  Error fetching ISSN {issn}: {e}")

print(f"Found {len(fetched_papers)} unique matching papers in 2025.")

# Write and Curate
added_count = 0
for doi, paper_data in fetched_papers.items():
    # Pre-screening guardrails
    is_flagged, flag_reason, evidence = guardrails.scan_paper(paper_data)
    if is_flagged:
        database.add_to_triage_queue(paper_data, flag_reason, evidence)
        continue
        
    added, updated = database.add_or_update_paper(paper_data)
    if added:
        # Get the database paper representation to obtain the newly generated paper ID
        conn = database.get_db_connection()
        p_row = conn.execute("select id from papers where doi = ?", (doi,)).fetchone()
        conn.close()
        if p_row:
            paper_data["id"] = p_row["id"]
            # Curate (which automatically generates the simulation script)
            review = agents_curator.curate_paper(paper_data)
            database.add_or_update_agent_review(review)
            added_count += 1
            print(f"Curated & Saved Paper ID {paper_data['id']}: {paper_data['title'][:50]}")

print(f"\nFinished. Crawled and curated {added_count} new 2025 papers with simulation files.")
