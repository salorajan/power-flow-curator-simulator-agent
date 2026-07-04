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
IEEE Power Publications & Grid Simulator MCP Server.
Implements the Model Context Protocol over stdio for external LLM integration.
"""
import sys
import os
import json
import sqlite3
import subprocess
import pandas as pd

# Discover paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
POWER_PROJECT_DIR = r"C:\users\robert\power\g5\project"
BATTERY_PROJECT_DIR = r"C:\Users\Robert\power\battery"
DB_PATH = os.path.join(PROJECT_ROOT, "papers.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper functions for tools
def tool_search_papers(query=None, journal=None, query_type=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM papers WHERE 1=1"
    params = []
    if journal:
        sql += " AND journal = ?"
        params.append(journal)
    if query_type:
        if query_type == "both":
            sql += " AND query_type = 'both'"
        else:
            sql += " AND (query_type = ? OR query_type = 'both')"
            params.append(query_type)
    if query:
        sql += " AND (title LIKE ? OR authors LIKE ? OR abstract LIKE ?)"
        like_pattern = f"%{query}%"
        params.extend([like_pattern, like_pattern, like_pattern])
        
    sql += " ORDER BY publication_date DESC LIMIT 50"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    papers = [dict(row) for row in rows]
    return {"papers": papers}

def tool_get_paper_review(doi):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_reviews WHERE doi = ?", (doi,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"error": f"No review found for DOI {doi}."}
    return dict(row)

def tool_run_power_flow(case_id, analysis_type):
    # Map input analysis_type
    analysis = analysis_type.lower()
    # Normalize case_id (e.g. '9' -> 'case9')
    full_case_name = case_id if case_id.startswith("case") else f"case{case_id}"
    
    # We will run the python command C:\users\robert\power\g5\project\power_cli.py
    cmd = [
        sys.executable,
        os.path.join(POWER_PROJECT_DIR, "power_cli.py"),
        case_id,
        analysis
    ]
    
    try:
        # Run process
        result = subprocess.run(
            cmd,
            cwd=POWER_PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        stdout = result.stdout
        stderr = result.stderr
        
        # Read the CSV files if successful
        output_prefix = f"{full_case_name}_{analysis}_results"
        results_dir = os.path.join(POWER_PROJECT_DIR, "results")
        bus_csv = os.path.join(results_dir, f"{output_prefix}_bus.csv")
        gen_csv = os.path.join(results_dir, f"{output_prefix}_gen.csv")
        branch_csv = os.path.join(results_dir, f"{output_prefix}_branch.csv")
        
        simulation_data = {}
        if os.path.exists(bus_csv):
            simulation_data["bus"] = pd.read_csv(bus_csv).to_dict(orient="records")[:30] # Cap size
        if os.path.exists(gen_csv):
            simulation_data["gen"] = pd.read_csv(gen_csv).to_dict(orient="records")
        if os.path.exists(branch_csv):
            simulation_data["branch"] = pd.read_csv(branch_csv).to_dict(orient="records")[:30] # Cap size
            
        return {
            "stdout": stdout,
            "stderr": stderr,
            "success": result.returncode == 0,
            "data": simulation_data
        }
    except Exception as e:
        return {"error": f"Power flow run failed: {str(e)}"}

def tool_simulate_solar_building(building_type, battery_cap=5000.0, solar_cap=1000.0, days=1):
    cmd = [
        sys.executable,
        os.path.join(BATTERY_PROJECT_DIR, "battery_cli.py"),
        "--type", building_type,
        "--battery-cap", str(battery_cap),
        "--solar-cap", str(solar_cap),
        "--days", str(days)
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=BATTERY_PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except Exception as e:
        return {"error": f"Solar building simulation failed: {str(e)}"}

# MCP stdio JSON-RPC loop
def main():
    # Make sure stdout uses line buffering and doesn't get stuck in a buffer block
    sys.stdout.reconfigure(line_buffering=True)
    
    while True:
        line = sys.stdin.readline()
        if not line:
            break
            
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        if not isinstance(req, dict):
            continue
            
        method = req.get("method")
        req_id = req.get("id")
        
        # Handle initialize
        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "ieee-power-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            continue
            
        if method == "notifications/initialized":
            continue
            
        # Handle resources/list
        if method == "resources/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": [
                        {
                            "uri": "power-papers://latest",
                            "name": "Latest Curated Papers",
                            "mimeType": "application/json",
                            "description": "The latest 10 publications fetched from IEEE Transactions on Power Systems."
                        },
                        {
                            "uri": "power-papers://statistics",
                            "name": "Publication Statistics",
                            "mimeType": "application/json",
                            "description": "Database metrics breakdown."
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            continue
            
        # Handle resources/read
        if method == "resources/read":
            params = req.get("params", {})
            uri = params.get("uri")
            content_text = ""
            if uri == "power-papers://latest":
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM papers ORDER BY publication_date DESC LIMIT 10")
                content_text = json.dumps([dict(row) for row in cursor.fetchall()], indent=2)
                conn.close()
            elif uri == "power-papers://statistics":
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM papers")
                total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM agent_reviews")
                reviews = cursor.fetchone()[0]
                content_text = json.dumps({"total_papers": total, "total_reviewed": reviews}, indent=2)
                conn.close()
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown resource URI: {uri}"
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
                continue
                
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": content_text
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            continue

        # Handle tools/list
        if method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "search_papers",
                            "description": "Search the indexed IEEE power system publications database by query and filters.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search keyword for title/authors/abstract"},
                                    "journal": {"type": "string", "description": "Specific journal name filter"},
                                    "query_type": {"type": "string", "description": "Query type: 'power flow', 'optimal power flow', or 'both'"}
                                }
                            }
                        },
                        {
                            "name": "get_paper_review",
                            "description": "Get the multi-agent academic peer-review card for a publication by its DOI.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "doi": {"type": "string", "description": "Digital Object Identifier (DOI) of the paper"}
                                },
                                "required": ["doi"]
                            }
                        },
                        {
                            "name": "run_power_flow",
                            "description": "Execute a power flow or optimal power flow simulation using PowerPython CLI on a standard bus case.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "case_id": {"type": "string", "description": "IEEE Case name (e.g., '6ww', '9', '118')"},
                                    "analysis_type": {"type": "string", "description": "Type of analysis: 'acpf', 'gausspf', 'fdpf', 'dcpf', 'hepf', 'dcopf', 'acopf', 'scopf', 'contingency'"}
                                },
                                "required": ["case_id", "analysis_type"]
                            }
                        },
                        {
                            "name": "simulate_solar_building",
                            "description": "Runs battery and solar PV dispatch optimization for a smart building and exports schedules.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "building_type": {"type": "string", "description": "Type of building: 'residential', 'commercial', 'dc' (datacenter), 'aidc'"},
                                    "battery_cap": {"type": "number", "description": "Battery storage capacity in kWh (default: 5000)"},
                                    "solar_cap": {"type": "number", "description": "Solar PV capacity in kW (default: 1000)"},
                                    "days": {"type": "integer", "description": "Number of simulation days (default: 1)"}
                                },
                                "required": ["building_type"]
                            }
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            continue
            
        # Handle tools/call
        if method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            tool_res = None
            if tool_name == "search_papers":
                tool_res = tool_search_papers(args.get("query"), args.get("journal"), args.get("query_type"))
            elif tool_name == "get_paper_review":
                tool_res = tool_get_paper_review(args.get("doi"))
            elif tool_name == "run_power_flow":
                tool_res = tool_run_power_flow(args.get("case_id"), args.get("analysis_type"))
            elif tool_name == "simulate_solar_building":
                tool_res = tool_simulate_solar_building(
                    args.get("building_type"),
                    args.get("battery_cap", 5000.0),
                    args.get("solar_cap", 1000.0),
                    args.get("days", 1)
                )
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {tool_name}"
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
                continue
                
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_res, indent=2)
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
            continue

        # Default fallthrough for unhandled requests
        res = {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
