# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Stage 2 Unit Tests for Multi-Agent Curation and Review System.
Verifies the curation process, scoring ranges, educational digest parsing,
and database persistence.
"""

import sys
import os
import json
import database
import agents_curator

def run_tests():
    print("--- Stage 2 Multi-Agent Curation Tests ---")
    
    # 1. Initialize DB
    database.init_db()
    
    # 2. Define Test Papers
    test_paper_convex = {
        "doi": "10.1109/TPWRS.2026.0000201",
        "title": "Convex Semidefinite Relaxation for Branch Flow AC-OPF",
        "authors": "Alice Green, Bob Brown",
        "abstract": "This study develops a semidefinite programming (SDP) relaxation for AC optimal power flow equations in radial distribution networks. We analyze conditions for zero relaxation gap and integrate battery energy storage system profiles.",
        "url": "https://doi.org/10.1109/TPWRS.2026.0000201",
        "journal": "IEEE Transactions on Power Systems",
        "query_type": "optimal power flow",
        "publication_date": "2026-06-10",
        "status": "Published"
    }
    
    test_paper_basic = {
        "doi": "10.1109/TPWRS.2026.0000202",
        "title": "A Standard Power Flow Study for Urban Distribution Systems",
        "authors": "Charlie White",
        "abstract": "We present load flow simulation studies for a city network using the standard Newton-Raphson method and discuss bus voltage limits.",
        "url": "https://doi.org/10.1109/TPWRS.2026.0000202",
        "journal": "IEEE Transactions on Power Delivery",
        "query_type": "power flow",
        "publication_date": "2026-06-11",
        "status": "Published"
    }
    
    # Clean previous test entries to ensure clean database state
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM papers WHERE doi LIKE '10.1109/TPWRS.2026.000020%'")
    cursor.execute("DELETE FROM agent_reviews WHERE doi LIKE '10.1109/TPWRS.2026.000020%'")
    conn.commit()
    conn.close()
    
    # Insert papers into the database
    database.add_or_update_paper(test_paper_convex)
    database.add_or_update_paper(test_paper_basic)
    
    # 3. Test Curation Logic (with Mock/Real API)
    print("Curating convex paper...")
    review_convex = agents_curator.curate_paper(test_paper_convex)
    print(f"Theory Score: {review_convex['theory_score']}")
    print(f"Grid Score: {review_convex['grid_score']}")
    
    assert review_convex['theory_score'] >= 1 and review_convex['theory_score'] <= 10
    assert review_convex['grid_score'] >= 1 and review_convex['grid_score'] <= 10
    assert "semidefinite" in review_convex['theory_review'].lower() or "sdp" in review_convex['theory_review'].lower()
    assert "battery" in review_convex['grid_review'].lower() or "bess" in review_convex['grid_review'].lower()
    
    # Save review to DB
    database.add_or_update_agent_review(review_convex)
    
    print("\nCurating basic paper...")
    review_basic = agents_curator.curate_paper(test_paper_basic)
    print(f"Theory Score: {review_basic['theory_score']}")
    print(f"Grid Score: {review_basic['grid_score']}")
    
    assert review_basic['theory_score'] >= 1 and review_basic['theory_score'] <= 10
    assert review_basic['grid_score'] >= 1 and review_basic['grid_score'] <= 10
    assert "newton-raphson" in review_basic['theory_review'].lower() or "fast decoupled" in review_basic['theory_review'].lower() or "steady-state" in review_basic['theory_review'].lower()
    
    # Save review to DB
    database.add_or_update_agent_review(review_basic)
    
    # 4. Verify Database Retrieval
    db_review_convex = database.get_agent_review(test_paper_convex['doi'])
    db_review_basic = database.get_agent_review(test_paper_basic['doi'])
    
    assert db_review_convex is not None
    assert db_review_basic is not None
    assert db_review_convex['theory_score'] == review_convex['theory_score']
    assert db_review_basic['grid_score'] == review_basic['grid_score']
    
    # Verify key acronyms parsing
    acronyms_convex = json.loads(db_review_convex['key_acronyms'])
    print("Convex Acronyms:", acronyms_convex)
    assert isinstance(acronyms_convex, dict)
    
    print("\nAll Stage 2 Tests Passed Successfully!")

if __name__ == "__main__":
    run_tests()
