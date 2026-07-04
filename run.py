import uvicorn
import sys
import os

# Support UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def main():
    # If starting with mcp argument, route execution to the MCP Server
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--mcp", "mcp"]:
        print("=========================================================")
        print("      IEEE Power Publications MCP Server Loading         ")
        print("=========================================================")
        print(" -> Mode: Model Context Protocol (stdio standard)")
        print(" -> Exposes: search_papers, get_paper_review,")
        print("            run_power_flow, simulate_solar_building")
        print("=========================================================")
        import mcp_server
        mcp_server.main()
        return

    print("=========================================================")
    print("      IEEE Power Publications Tracker Server Loading     ")
    print("=========================================================")
    print(" -> Backend API & Frontend GUI will be available at:")
    print("    URL: http://127.0.0.1:8000")
    print(" -> Database file: papers.db")
    print(" -> Hit Ctrl+C to terminate the server")
    print("=========================================================")
    
    # Run uvicorn server. Reload is set to True to help with iterations.
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
