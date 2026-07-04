# IEEE Power Grid Publications Curation Agent & Simulator Portal: User Manual

This manual provides detailed instructions on how to configure, run, and interact with the curation agents, safety guardrails, MCP server, and interactive simulators.

---

## 1. Safety and Secrets Management: Gemini API Key

To use the Google Gemini developer API for live, high-fidelity publication curation:
1. **No Hardcoded Keys:** To adhere to security guidelines, do not hardcode your API key anywhere in the codebase.
2. **Local Environment Variables:** You can set the key in the following ways depending on your platform:

### Option A: Using a `.env` file (Recommended for Local Dev)
Create a file named `.env` in the project root directory (`agy-cli-projects/`) and add your key:
```env
GEMINI_API_KEY=AIzaSyYourActualKeyHere
```
*Note: The `.env` file is excluded in `.gitignore` to prevent leaking it to GitHub.*

### Option B: Using System Environment Variables
* **Windows (PowerShell):**
  ```powershell
  $env:GEMINI_API_KEY="AIzaSyYourActualKeyHere"
  ```
* **Windows (Command Prompt):**
  ```cmd
  set GEMINI_API_KEY=AIzaSyYourActualKeyHere
  ```
* **Linux/macOS:**
  ```bash
  export GEMINI_API_KEY="AIzaSyYourActualKeyHere"
  ```

*Fallback Mode:* If no `GEMINI_API_KEY` is detected, the curation engine will automatically switch to a high-fidelity local rule-based mock engine. This allows full testing and portal operation offline.

---

## 2. Launching the Web Portal

Run the FastAPI backend launcher from the project root:
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:8000`.

### Web Dashboard Workflows:

#### A. Ingesting Publications (Fetcher)
1. On the main page, view the list of fetched papers in the **Publications Index**.
2. To trigger a new query to Crossref, click **Trigger Ingestion Scan**.
3. The backend crawls IEEE Transactions on Power Systems publications matching your keyword configuration.
4. Any paper abstract that contains suspicious text or command overrides triggers the security guardrails and is sent to the **Triage Queue**.

#### B. Curation Panel (Theory / Grid / Educational consensus)
1. Click on any paper in the Publications list.
2. Click the **Curate** button to activate the Multi-Agent Panel.
3. Once completed, browse the tabbed cards:
   * **Theory Review:** Rigor rating and assessment of formulation type (e.g. AC vs. DC, SOCP/SDP approximation).
   * **Grid Impact:** Evaluation of practical grid utility, DER/BESS dispatch scheduling, and decarbonization capability.
   * **Educational Digest:** Prerequisites glossary, student takeaways, and defined key acronyms.

#### C. HITL Triage Queue
1. Switch to the **Triage Queue** tab.
2. Here, you will see quarantined papers. Each card lists the flag reason (e.g. `Guardrail Violation`) and the evidence segment that triggered it.
3. Review the title/abstract and click **Approve Ingestion** (inserts into the main index) or **Reject Paper** (discards it).

#### D. Grid Flow & Battery Simulator
1. Switch to the **Grid Simulator** tab.
2. In the **Control Panel (Left)**:
   * Select a Case bus study (e.g., `9-bus`, `6-bus`, `118-bus`).
   * Select a Solver method (Newton-Raphson `acpf`, Gauss-Seidel `gausspf`, DC Power Flow `dcpf`, Holomorphic Embedding `hepf`, etc.).
   * Click **Run Simulator**.
3. In the **Results Panel (Right)**:
   * View stdout convergence logs.
   * Read the Bus voltage table. Voltages outside the safety threshold `0.95 - 1.05 pu` will highlight in red to flag grid instability.
4. To simulate BESS scheduling, choose load types (Commercial/Residential), adjust solar PV capacity, and run a **Solar Storage Dispatch** optimization.

---

## 3. Running the MCP Server
To expose the papers database, review reports, and power grid simulation tools to external LLM environments (like Google Antigravity or Cursor):
```bash
python run.py --mcp
```
This boots a JSON-RPC stdio protocol server. You can integrate this with your MCP client using the standard configuration:
```json
{
  "mcpServers": {
    "ieee-power-coordinator": {
      "command": "python",
      "args": ["C:/users/robert/power/g5/agy-cli-projects/run.py", "--mcp"]
    }
  }
}
```

---

## 4. Running Individual Paper Simulations
The agent automatically writes a runnable Python simulation script for every curated publication.
1. Browse to the [simulations/](file:///C:/users/robert/power/g5/agy-cli-projects/simulations) folder.
2. Run any simulation script directly:
   ```bash
   python simulations/simulate_paper_14.py
   ```
3. The script will execute the PowerPython solver specific to that paper's methodology and output active constraints, solar profiles, and grid thermal balance.

---

## 5. Verification Test Suite
To verify the system integrity locally, run the stage test runners:
```bash
# Security & DB Routing Verification
python -m scratch.test_stage1

# Curation Consensus Panel Verification
python -m scratch.test_stage2

# MCP Tool Executions Verification
python -m scratch.test_stage3
```
All stage suites should report successful passes.
