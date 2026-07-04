import database
import agents_curator

conn = database.get_db_connection()
papers = conn.execute("select id, doi, title, authors, abstract, url, journal, query_type, publication_date, volume, issue, status, fetched_at from papers").fetchall()
conn.close()

print(f"Re-curating all {len(papers)} papers in database...")
for idx, row in enumerate(papers):
    paper_data = dict(row)
    review = agents_curator.curate_paper(paper_data)
    database.add_or_update_agent_review(review)
    print(f"[{idx+1}/{len(papers)}] Re-curated ID {paper_data['id']}: {paper_data['title'][:50]}")

print("All papers successfully re-curated with simulation scripts generated.")
