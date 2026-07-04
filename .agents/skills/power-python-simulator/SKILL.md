---
name: power-python-simulator
description: Simulates steady-state power flow (PF) and optimal power flow (OPF) on IEEE case studies (e.g., 6ww, 9, 118) using the PowerPython suite.
---

# PowerPython Simulator Skill

This skill allows the agent to run steady-state power flow and optimal power flow optimizations on power grids using the local `PowerPython` CLI tool.

## Key Information
*   **CLI Path**: [power_cli.py](file:///C:/users/robert/power/g5/project/power_cli.py)
*   **Execution Directory**: `C:\users\robert\power\g5\project`
*   **Available Cases**: Standard case numbers/IDs (e.g., `6ww`, `9`, `118`).
*   **Output Files**: The CLI exports results to the `results/` folder as CSVs:
    *   `<case>_<analysis>_results_bus.csv` (voltage magnitude/angles, load values)
    *   `<case>_<analysis>_results_gen.csv` (active/reactive power generation dispatch)
    *   `<case>_<analysis>_results_branch.csv` (transmission line flows)

## Instructions

1.  **Run Simulations**:
    To run any simulation, execute the CLI using `run_command` in the `C:\users\robert\power\g5\project` directory.
    
    ```bash
    python power_cli.py <case_id> <analysis_type> [--enforce-q-limits]
    ```

    *Example (Newton-Raphson ACPF on Case 9)*:
    ```bash
    python power_cli.py 9 acpf
    ```

    *Example (AC Optimal Power Flow on Case 6ww enforcing generator reactive limits)*:
    ```bash
    python power_cli.py 6ww acopf --enforce-q-limits
    ```

2.  **Supported Solvers (`<analysis_type>`)**:
    *   **`acpf` / `pf`**: AC Power Flow (Newton-Raphson)
    *   **`gausspf` / `gs`**: Gauss-Seidel AC Power Flow
    *   **`fdpf` / `fd`**: Fast Decoupled AC Power Flow
    *   **`dcpf`**: DC Power Flow (Linearized approximation)
    *   **`dcopf`**: DC Optimal Power Flow (Cost minimization)
    *   **`acopf`**: AC Optimal Power Flow (Non-linear cost & flow optimization)
    *   **`hepf`**: Holomorphic Embedding (State-of-the-art non-iterative AC solver)
    *   **`scopf`**: Security-Constrained OPF (N-1 Secure dispatch)
    *   **`cpf`**: Continuation Power Flow (Traces PV curves/voltage collapse bounds)
    *   **`contingency` / `cont`**: N-1 Contingency Analysis

3.  **Read and Verify Results**:
    After successful execution, check the generated results CSV files in the `results/` directory of the project to verify voltage boundaries, line flow limits, or generation costs. Do not try to guess solver outcomes.
