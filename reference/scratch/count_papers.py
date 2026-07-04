# Scratch script to count papers in sqlite
import database

conn = database.get_db_connection()
total = conn.execute("select count(*) from papers").fetchone()[0]
total_2026 = conn.execute("select count(*) from papers where publication_date like '2026%'").fetchone()[0]
print(f"TOTAL_PAPERS: {total}")
print(f"TOTAL_2026_PAPERS: {total_2026}")

# Let's count how many 2026 papers are already curated (i.e. exist in agent_reviews)
curated_2026 = conn.execute("""
    select count(*) from papers p 
    join agent_reviews r on p.doi = r.doi 
    where p.publication_date like '2026%'
""").fetchone()[0]
print(f"CURATED_2026_PAPERS: {curated_2026}")

# Get list of uncurated 2026 papers
uncurated_2026_list = conn.execute("""
    select p.id, p.title from papers p 
    left join agent_reviews r on p.doi = r.doi 
    where p.publication_date like '2026%' and r.id is null
""").fetchall()

print(f"UNCURATED_2026_COUNT: {len(uncurated_2026_list)}")
conn.close()
