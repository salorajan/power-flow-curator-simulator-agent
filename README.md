# IEEE Power Grid Publications Curation Agent & Simulator Portal

[![Capstone Project Status](https://img.shields.io/badge/Capstone-Complete-success.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.14-blue.svg)](#)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](#)

This repository contains the **IEEE Power Grid Publications Curation Agent & Simulator Portal**, submitted as the Capstone Project for the *5-Day AI Agents: Intensive Vibe Coding Course With Google*. 

---

## 📖 Project Overview & Mission

### Selected Track: **Agents for Good** (Education & Grid Decarbonization Research)

Grid decarbonization requires complex mathematical models—such as AC/DC Optimal Power Flow and Holomorphic Embedding—to integrate Distributed Energy Resources (DERs) like rooftop solar and Battery Energy Storage Systems (BESS). However, these models are scattered across thousands of academic publications.

Our portal bridges the gap between scientific literature and active engineering simulations:
1. **Automated Ingestion:** Crawls Crossref for latest publications from core IEEE Transactions journals.
2. **Security Guardrails:** Pre-screens crawled abstracts for prompt injections or adversarial structures.
3. **Multi-Agent Consensus Panel:** Evaluates the mathematical formulation (Theory Agent), practical grid utility (Grid Agent), and summarizes prerequisites for students (Educational Digest Agent).
4. **Curation-Linked Simulations:** During curation, the agents automatically generate a dedicated, runnable Python script mapping the paper's theoretical methodology directly to local power grid and battery optimizers.
5. **Model Context Protocol (MCP):** Exposes all database papers, reviews, and simulator execution tools as an MCP standard server over stdio for external agent environments.
6. **Frontend UI Dashboard:** A modern, dark glassmorphic portal to trigger curation, triage quarantined papers, configure battery parameters, run grid flow studies, and view bus voltage results.

---

## 📂 Project Directory Structure

The project has been organized into a clean, modular repository layout:

```text
agy-cli-projects/
├── .agents/                # Custom local agent skills
├── reference/              # Documentation and scratch scripts
│   ├── capstone.txt        # Course capstone requirements
│   ├── plan.md             # Original project plan
│   ├── project_implementation.md  # Detailed implementation log
│   ├── papers_schema.sql   # SQL database schema reference
│   └── scratch/            # Temporary curation & count scripts
├── scratch/                # Unit test suites
│   ├── test_stage1.py      # Database routing & guardrail tests
│   ├── test_stage2.py      # Multi-agent curation panel tests
│   └── test_stage3.py      # MCP tool & simulator test suite
├── simulations/            # Generated Python simulation scripts (77 files)
├── static/                 # Glassmorphic web frontend UI assets
│   ├── index.html          # Main UI layout
│   ├── style.css           # Neon dark-theme styling
│   └── app.js              # State manager and API client
├── agents_curator.py       # Curation agent logic (Theory/Grid/Educational)
├── backend.py              # FastAPI web server APIs
├── database.py             # SQLite database layer
├── fetcher.py              # Crossref publication crawler
├── guardrails.py           # Input security guardrail pre-screening
├── mcp_server.py           # Custom Model Context Protocol (stdio standard)
├── papers.db               # SQLite database file containing 77 papers
├── run.py                  # Main project entrypoint launcher
└── README.md               # GitHub-style project readme (this file)
```

---

## 🛠️ Installation & Setup

1. **Prerequisites:**
   Ensure you are using the `env_power` virtual environment.
   
2. **Database Initialization:**
   The SQLite database (`papers.db`) is automatically initialized and loaded with 77 curated papers from 2025–2026.

3. **Gemini API Key Configuration:**
   To enable live Gemini-powered curation reviews, set your API key using one of the following methods:
   * **Option A (.env file):** Create a `.env` file in the project root directory:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
   * **Option B (System Environment Variable):**
     * *Windows (PowerShell):* `$env:GEMINI_API_KEY="your_api_key"`
     * *Windows (Command Prompt):* `set GEMINI_API_KEY=your_api_key`
     * *Linux/macOS:* `export GEMINI_API_KEY="your_api_key"`

   *Note: If no API key is specified, the application will automatically fall back to its high-fidelity local rule-based mock reviews engine, remaining 100% functional and testable. No keys or passwords are hardcoded or shared in the repository.*

4. **Detailed Documentation & User Manual:**
   Refer to the comprehensive [reference/user_manual.md](file:///C:/users/robert/power/g5/agy-cli-projects/reference/user_manual.md) for step-by-step guidance on running the FastAPI Dashboard, the stdio MCP Server, generated paper simulations, and the verification test suite.


---

## 🚀 How to Run the Project

### 1. Launch the Web Portal
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:8000` to interact with:
* **Publications Index:** Browse and trigger new crawls.
* **Curation Panel:** Click "Curate" to trigger the multi-agent consensus panel and read review cards.
* **HITL Triage Queue:** Inspect flagged abstracts and approve or reject their ingestion.
* **Grid Simulator:** Run Newton-Raphson, Holomorphic Embedding, or radial distribution load flows on IEEE Case studies and observe bus voltage safety warnings.

### 2. Launch the MCP Server
```bash
python run.py --mcp
```
Connect this stdio-based server to any MCP client (such as Cursor, Windsurf, or Google Antigravity) to let external agents query your curated literature and execute solvers.

### 3. Run Individual Paper Simulations
Every paper in the database has a dedicated Python simulation script under the `simulations/` directory. To simulate the mathematical methodology of any paper (e.g. Paper ID 14), run:
```bash
python simulations/simulate_paper_14.py
```
This runs the local power flow solver and prints convergence rates and safety violations.

---

## 🧪 Running the Verification Test Suite

You can execute the verification test suite to ensure the system is fully functional:

```bash
# Verify Stage 1: Security Guardrails & DB Routing
python -m scratch.test_stage1

# Verify Stage 2: Multi-Agent Curation Panel
python -m scratch.test_stage2

# Verify Stage 3: MCP Server, Solvers, and Subprocess executions
python -m scratch.test_stage3
```

---

## 📚 Credits & Acknowledgments

* **PowerPython Solver Engine:** Inspired by the MATPOWER ecosystem, porting core solver logic to the modern NumPy/SciPy stack.
* **pvlib & CVXPY:** Used for commercial/residential clear-sky PV modeling and chance-constrained BESS battery scheduling optimization.
