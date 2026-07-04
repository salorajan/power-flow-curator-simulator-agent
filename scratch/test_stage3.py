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
Stage 3 Unit Tests for Model Context Protocol (MCP) Server.
Tests standard stdio JSON-RPC initialization, resource listing, tool listing,
and simulation tool calls.
"""

import sys
import os
import json
import subprocess

def run_tests():
    print("--- Stage 3 MCP Server Tests ---")
    
    server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server.py")
    
    # Start the MCP server in a subprocess
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    def send_and_receive(req):
        payload = json.dumps(req) + "\n"
        proc.stdin.write(payload)
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line)

    try:
        # 1. Test Initialize Method
        print("Testing 'initialize' request...")
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "TestClient", "version": "1.0"}
            }
        }
        res = send_and_receive(init_req)
        print("Initialize Response:", json.dumps(res, indent=2))
        assert res.get("id") == 1
        assert "protocolVersion" in res.get("result", {})
        assert res["result"]["serverInfo"]["name"] == "ieee-power-mcp-server"
        
        # 2. Test Tools List Method
        print("\nTesting 'tools/list' request...")
        tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        res = send_and_receive(tools_req)
        tools = res.get("result", {}).get("tools", [])
        print("Exposed Tools:")
        for t in tools:
            print(f"  - {t['name']}: {t['description']}")
            
        tool_names = [t["name"] for t in tools]
        assert "search_papers" in tool_names
        assert "get_paper_review" in tool_names
        assert "run_power_flow" in tool_names
        assert "simulate_solar_building" in tool_names
        
        # 3. Test Resources List Method
        print("\nTesting 'resources/list' request...")
        resources_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list"
        }
        res = send_and_receive(resources_req)
        resources = res.get("result", {}).get("resources", [])
        print("Exposed Resources:")
        for r in resources:
            print(f"  - {r['uri']}: {r['name']}")
        assert len(resources) >= 2
        
        # 4. Test Search Papers Tool Call
        print("\nTesting 'tools/call' for search_papers...")
        search_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "search_papers",
                "arguments": {"query": "power"}
            }
        }
        res = send_and_receive(search_req)
        content_block = json.loads(res["result"]["content"][0]["text"])
        papers = content_block.get("papers", [])
        print(f"Found {len(papers)} papers using search.")
        assert len(papers) > 0
        
        # 5. Test Power Flow Tool Call (Newton-Raphson on Case 9)
        print("\nTesting 'tools/call' for run_power_flow (Newton-Raphson on Case 9)...")
        pf_req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "run_power_flow",
                "arguments": {"case_id": "9", "analysis_type": "acpf"}
            }
        }
        res = send_and_receive(pf_req)
        pf_block = json.loads(res["result"]["content"][0]["text"])
        print(f"Power Flow Success: {pf_block.get('success')}")
        assert pf_block.get("success") is True
        assert "bus" in pf_block.get("data", {})
        assert "gen" in pf_block.get("data", {})
        assert "branch" in pf_block.get("data", {})
        
        # 6. Test Solar Building Simulation
        print("\nTesting 'tools/call' for simulate_solar_building (residential)...")
        solar_req = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "simulate_solar_building",
                "arguments": {"building_type": "residential", "days": 1}
            }
        }
        res = send_and_receive(solar_req)
        solar_block = json.loads(res["result"]["content"][0]["text"])
        print(f"Solar Dispatch Success: {solar_block.get('success')}")
        assert solar_block.get("success") is True
        
        print("\nAll Stage 3 MCP Server Tests Passed Successfully!")
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    run_tests()
