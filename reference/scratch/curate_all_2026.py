import database
import agents_curator

# Establish DB connection
conn = database.get_db_connection()

# Get all uncurated 2026 papers
uncurated_papers = conn.execute("""
    select p.id, p.doi, p.title, p.authors, p.abstract, p.url, p.journal, p.query_type, p.publication_date, p.volume, p.issue, p.status, p.fetched_at 
    from papers p 
    left join agent_reviews r on p.doi = r.doi 
    where p.publication_date like '2026%' and r.id is null
""").fetchall()

print(f"Starting batch curation for {len(uncurated_papers)} papers...")

count = 0
for row in uncurated_papers:
    paper_data = dict(row)
    try:
        # Curate paper (this dynamically generates simulate_paper_<id>.py)
        review = agents_curator.curate_paper(paper_data)
        database.add_or_update_agent_review(review)
        count += 1
        print(f"[{count}/{len(uncurated_papers)}] Curated ID {paper_data['id']}: {paper_data['title'][:50]}")
    except Exception as e:
        print(f"Error curating ID {paper_data['id']}: {e}")

conn.close()
print(f"Finished. Successfully curated {count} papers and generated their simulation scripts.")
