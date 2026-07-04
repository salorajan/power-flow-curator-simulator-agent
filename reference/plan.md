# IEEE Power Publications Tracker & Curation Agent (Kaggle Capstone Project)

> [!IMPORTANT]
> **Project Status: Phase 1, 2, 3, and 4 Completed.** Database schema, guardrail pre-screening, Multi-Agent Curation logic, lightweight stdio MCP Server, and premium frontend UI views are fully integrated, tested, and passing all unit tests.
> **Next Action (To Be Continued):** **Comprehensive Testing Phase.** Focus on UAT validation, edge-case debugging, database integrity under high load, and live validation using external MCP clients.

This document outlines the project plan, architecture, and roadmap for the **IEEE Power Publications Tracker & Curation Agent**, configured as a submission for the **Kaggle 5-Day AI Agents Intensive Vibe Coding Capstone Project**.

---


## 1. Capstone Project Meta Information

*   **Project Track:** **Agents for Good**
*   **Track Focus:** Education & Grid Decarbonization Research.
*   **Problem Statement:** Optimal Power Flow (OPF) and Power Flow (PF) are crucial mathematical frameworks for integrating renewable energy and optimizing grid efficiency to reduce carbon emissions. However, the volume of scientific literature is massive, making it difficult for students and researchers to quickly digest theoretical models, assess practical grid utility, and extract educational value.
*   **Our Solution:** An agentic educational research portal that automatically fetches power systems papers, conducts multi-agent peer reviews from distinct academic and practical perspectives, and serves this knowledge base to the wider community via a Web Dashboard and a dedicated Model Context Protocol (MCP) server.
*   **Solar Grid Integration Feature:** Instead of general wind and solar modeling, this project integrates standard solar PV and battery storage dispatch for **Smart Buildings** interacting with the grid. It leverages existing local optimization libraries to simulate building BESS scheduling and analyze grid impacts using power flow algorithms.

---

## 2. Key Course Concepts Demonstrated

To meet the capstone criteria, this project implements three core concepts from the Kaggle 5-Day Vibe Coding syllabus:

### A. Multi-Agent Collaboration & Cognitive Architecture (Days 2 & 3)
Instead of generic summarization, each ingested paper is subjected to a specialized peer-review panel consisting of three agent personas:
1.  **Theory & Mathematical Formulation Agent:** Evaluates the power flow model rigor (e.g., AC vs. DC, convex approximations like SOCP/SDP, linearizations) and mathematical proofs.
2.  **Grid Impact & Sustainability Agent:** Assesses the practical utility, computational viability, and potential to facilitate solar-building integration or battery dispatch.
3.  **Educational Digest Agent:** Normalizes the paper into an accessible summary for students, defining prerequisites (e.g., Newton-Raphson, OPF basics) and key acronyms.

*Memory Integration:* The agents share a short-term conversational context to debate and compile a unified, structured **Academic Review Card** saved directly to the database.

### B. Model Context Protocol (MCP) Server (Day 2)
We implement a custom **IEEE Power Publications MCP Server** ([mcp_server.py](file:///C:/users/robert/power/g5/agy-cli-projects/mcp_server.py)) that exposes the curated database and local simulation features to the wider LLM developer ecosystem. 
*   **Resources:** Exposes the indexed papers and stats as read-only resources (e.g., `power-papers://latest`, `power-papers://statistics`).
*   **Tools:** Exposes search functions (`search_papers`), curation triggers (`get_paper_review`), and simulator bindings (`run_power_flow`).
*   This enables external agents (like Google Antigravity or other client systems) to consume our structured data and interact with our database dynamically.

### C. Security Guardrails & Human-in-the-Loop (HITL) Triage (Day 4)
Scientific abstract feeds and user search parameters can contain prompt injections or malicious instructions. We enforce security best practices:
1.  **Content Guardrails:** A preprocessing check that scans crawled papers' title/abstract metadata and user search parameters for jailbreaks or instructions targeting our curation agents.
2.  **HITL Admin Triage Dashboard:** If a paper triggers a security warning or the multi-agent panel flags a paper as highly speculative/low-confidence, it is marked as `Pending Triage`. The admin must explicitly review and approve or reject it from the dashboard before it is listed in the main database or served over MCP.

---

## 3. Workspace-Scoped Agent Skills Integration

We integrate 5 custom workspace-scoped skills imported from the local tutorial repository [skills_tutorial](file:///C:/Users/Robert/power/g5/antigravity-skills/skills_tutorial/.agents/skills) to extend the capabilities of the agent and standard development workflows:

1.  **`power-python-simulator`**:
    *   **Purpose:** Allows agents to run steady-state power flow (ACPF, Gauss-Seidel, FDPF, DCPF, Holomorphic Embedding) and optimal power flow (ACOPF, DCOPF, SCOPF) optimizations using the `PowerPython` CLI suite.
    *   **Smart Building Solar-Battery Integration:** Uses local libraries to calculate solar-battery building dispatches, map them as generation/load profiles in the IEEE grids (e.g., Case 9, 6ww), and simulate their voltage and thermal impact.
2.  **`database-schema-validator`**:
    *   **Purpose:** Ensures any schema modifications (e.g., adding `agent_reviews` and `triage_queue` tables) strictly adhere to database conventions (e.g., `snake_case`, `id` PRIMARY KEY, no raw `DROP TABLE`).
3.  **`git-commit-formatter`**:
    *   **Purpose:** Enforces structured, standard Git commit messages under the Conventional Commits specification.
4.  **`license-header-adder`**:
    *   **Purpose:** Automatically appends standard copyright/licensing notices to new files generated during coding (`guardrails.py`, `agents_curator.py`, `mcp_server.py`).
5.  **`json-to-pydantic`**:
    *   **Purpose:** Converts API responses (e.g., Crossref schemas, simulator CSV models) into robust Pydantic data models for FastAPI request-response parsing.

---

## 4. Custom Local Optimization Libraries

To build the solar panels, battery dispatch, and smart grid simulation components, we utilize existing local modules:
*   **Battery Scheduling System ([power/battery](file:///C:/Users/Robert/power/battery)):** Implements chance-constrained BESS charging/discharging algorithms under grid network cases. Supports stochastic solar and load forecasting profiles.
*   **DER Building Optimizer ([power/der](file:///C:/Users/Robert/power/der)):** Implements DABEO (DER-Aware Building Energy Optimizer) which models solar panels via `pvlib` and performs cost-minimization dispatch optimization under time-of-use tariffs via `cvxpy`.

---

## 5. Updated Technical Stack
*   **Virtual Environment:** `env_power` (Python 3.14.4)
*   **Backend Web Framework:** FastAPI (Uvicorn server)
*   **Database:** SQLite3 (`papers.db`)
*   **Optimization Solvers:** CVXPY (for BESS/DER dispatch scheduling)
*   **Solar Modeling Engine:** pvlib (CEC module/inverter calculations, clear sky irradiance, solar position)
*   **AI Agent Framework:** Agent Development Kit (ADK) / Google AI Studio API
*   **Protocol Layer:** Model Context Protocol (MCP) Python SDK
*   **Simulation Suite:** `PowerPython` CLI (Newton-Raphson, GS, Fast Decoupled, HEMP, ACOPF, DCOPF, Contingency analysis)
*   **Frontend UI:** Vanilla HTML5, CSS3 (Modern Glassmorphic Dark Theme with Neon Accents), and JavaScript (ES6)

---

## 6. Architecture & File Catalog

We will expand the existing architecture to integrate the agentic components:

### Core Files
*   [backend.py](file:///C:/users/robert/power/g5/agy-cli-projects/backend.py): Serves the Web UI and API endpoints. We will add endpoints for triggering/reviewing agent evaluations, running grid simulations, and the HITL triage queue.
*   [database.py](file:///C:/users/robert/power/g5/agy-cli-projects/database.py): Manages connections to `papers.db`. Needs to be updated to support the new `agent_reviews` and `triage_queue` tables.
*   [fetcher.py](file:///C:/users/robert/power/g5/agy-cli-projects/fetcher.py): Interacts with the Crossref API, handles keyword filtering, and applies the security guardrail pre-screening.
*   [run.py](file:///C:/users/robert/power/g5/agy-cli-projects/run.py): Main entry point to launch both the FastAPI backend and the MCP server.

### New Agentic & Logging Files
*   [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md): **(Critical)** Tracks implementation progress, success/failure logs, design modifications, and step-by-step validation.
*   [mcp_server.py](file:///C:/users/robert/power/g5/agy-cli-projects/mcp_server.py): Defines the custom MCP server exposing tools and resources for external agent consumption.
*   [agents_curator.py](file:///C:/users/robert/power/g5/agy-cli-projects/agents_curator.py): Implements the multi-agent consensus panel (Theory, Grid Impact, and Educational Digest agents) using Google AI Studio.
*   [guardrails.py](file:///C:/users/robert/power/g5/agy-cli-projects/guardrails.py): Implements input classification logic to detect adversarial prompt injection and safety violations in crawled metadata or user-facing fields.

### Frontend Dashboard
*   [static/index.html](file:///C:/users/robert/power/g5/agy-cli-projects/static/index.html): Glassmorphic UI dashboard. Will be updated to show:
    *   **Agent Curation Panel:** Tabs for Theory, Grid Impact, and Educational Digest reviews for selected papers.
    *   **HITL Admin Panel:** A secure tab to approve/reject flagged papers from the `triage_queue`.
    *   **Interactive Grid Simulator:** A control panel allowing users to trigger standard IEEE grid simulations, configure building solar PV/battery capacities, and view active dispatches and voltage statistics.
*   [static/style.css](file:///C:/users/robert/power/g5/agy-cli-projects/static/style.css): Main CSS stylesheet. Custom glassmorphic cards, custom tabs, status indicators, and clean animations.
*   [static/app.js](file:///C:/users/robert/power/g5/agy-cli-projects/static/app.js): Handles dashboard updates, modal interactions, API polling for paper updates, grid simulation executions, and user triage commands.

---

## 7. SQLite3 Database Schema (`papers.db`)

We expand the DB schema to handle agent curation reviews and security flags:

### A. Existing Tables (Updated)
*   **`papers`**: Stores clean matching papers. We will add a reference to check if a paper has an associated multi-agent review.
*   **`update_logs`**: Tracks crawl execution metadata.

### B. New Tables
#### `agent_reviews` Table
Stores the structured outputs of the multi-agent consensus panel.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key (Autoincrement) |
| `doi` | TEXT | Unique DOI referencing the paper |
| `theory_review` | TEXT | Markdown summary of the mathematical model analysis |
| `theory_score` | INTEGER | Mathematical rigor score (1-10) |
| `grid_review` | TEXT | Practical grid impact & sustainability review |
| `grid_score` | INTEGER | Grid applicability score (1-10) |
| `educational_digest` | TEXT | Accessible summary with student-friendly explanations |
| `key_acronyms` | TEXT | JSON string of defined acronyms/terms |
| `curated_at` | TEXT | Timestamp of the agent review generation |

#### `triage_queue` Table
Handles human-in-the-loop triaging for papers flagged by guardrails or agents.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key (Autoincrement) |
| `doi` | TEXT | Paper DOI |
| `flag_reason` | TEXT | Reason for flag (e.g. `'Guardrail Violation'`, `'Low Quality Score'`, `'Potential Injection'`) |
| `evidence` | TEXT | Text segment that triggered the warning |
| `status` | TEXT | `'pending'`, `'approved'`, or `'rejected'` |
| `reviewed_at` | TEXT | Timestamp of human triage decision |

---

## 8. Implementation Roadmap & Stage-by-Stage Evaluation Protocol

Every phase must be strictly evaluated. The results, failures, successes, and modifications must be logged in [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md) before moving to the next stage.

### Phase 1: Workspace Import & Security Guardrails [COMPLETED 2026-06-20]
1.  Import (copy) the `.agents` folder from the `skills_tutorial` repository into the project root `agy-cli-projects/` so that the 5 custom skills are active in the local workspace. (Done)
2.  Extend [database.py](file:///C:/users/robert/power/g5/agy-cli-projects/database.py) with `agent_reviews` and `triage_queue` schemas. (Done)
3.  Develop [guardrails.py](file:///C:/users/robert/power/g5/agy-cli-projects/guardrails.py) with simple keyword and semantic rule classifiers to flag potential prompt injections in abstracts. (Done)
4.  Modify [fetcher.py](file:///C:/users/robert/power/g5/agy-cli-projects/fetcher.py) to run raw papers through `guardrails.py` and route them either directly to `papers` or to the `triage_queue`. (Done)
5.  *Evaluation Gateway:* Run schema validation using the `database-schema-validator` skill and verify guardrail detection accuracy. Record findings in [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md). (Done - Schema validation passed, unit tests passed).


### Phase 2: Multi-Agent Curation System
1.  Implement [agents_curator.py](file:///C:/users/robert/power/g5/agy-cli-projects/agents_curator.py) to structure the Theory, Grid Impact, and Educational Digest agents.
2.  Configure prompt templates to force detailed, structured evaluations.
3.  Add API endpoints in [backend.py](file:///C:/users/robert/power/g5/agy-cli-projects/backend.py) to trigger evaluations:
    *   `POST /api/papers/{id}/curate`: Starts the agent consensus panel.
    *   `GET /api/papers/{id}/review`: Retrieves the completed academic review.
4.  *Evaluation Gateway:* Test multi-agent responses against 3 sample papers, evaluating response speed and theoretical scoring accuracy. Record in [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md).

### Phase 3: Model Context Protocol (MCP) Server Setup & Solar building Simulator
1.  Create [mcp_server.py](file:///C:/users/robert/power/g5/agy-cli-projects/mcp_server.py) using the python `mcp` SDK.
2.  Expose the `battery` and `der` library functions as a core simulation tool.
3.  Register tools:
    *   `search_papers`: searches publication DB.
    *   `get_paper_review`: returns multi-agent review for a given paper.
    *   `run_power_flow`: routes simulation commands to `power-python-simulator` CLI execution and returns output JSON.
    *   `simulate_solar_building`: runs the CVXPY/pvlib dispatch optimization for a smart building and exports charging profiles to the power flow solver.
4.  Configure [run.py](file:///C:/users/robert/power/g5/agy-cli-projects/run.py) to allow starting the app with the MCP server attached.
5.  *Evaluation Gateway:* Verify MCP tool registration and run a test simulation command from a mock agent client. Record in [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md).

### Phase 4: UI Dashboard Curation, HITL & Simulator Extension
1.  Update [static/index.html](file:///C:/users/robert/power/g5/agy-cli-projects/static/index.html) and [static/app.js](file:///C:/users/robert/power/g5/agy-cli-projects/static/app.js) to display agent reviews inside the paper detail modal.
2.  Design a sleek HITL Admin Panel tab with modern styling in [static/style.css](file:///C:/users/robert/power/g5/agy-cli-projects/static/style.css) to list, approve, and reject flagged publications in real-time.
3.  Incorporate the solar smart building simulation controls into the dashboard so users can run battery optimization dispatch curves (based on the `der` and `battery` codebases) and view grid impact results.
4.  *Evaluation Gateway:* Perform final user-acceptance tests (UAT) for frontend integration, verifying UI responsiveness and data consistency. Record in [project_implementation.md](file:///C:/users/robert/power/g5/agy-cli-projects/project_implementation.md).
