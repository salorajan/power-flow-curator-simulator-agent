from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import database
import fetcher
import agents_curator

app = FastAPI(
    title="IEEE Power Publications Tracker API",
    description="Backend API to search and store publications from IEEE Transactions on Power Systems, Power Delivery, and Smart Grid.",
    version="1.0.0"
)

# CORS configuration to allow local frontend development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/api/papers")
def get_papers(
    journal: str = Query(None),
    query_type: str = Query(None),
    status: str = Query(None),
    search: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Returns a paginated list of publications matching the filters and search query.
    """
    filters = {}
    if journal:
        filters['journal'] = journal
    if query_type:
        filters['query_type'] = query_type
    if status:
        filters['status'] = status
        
    try:
        papers, total = database.get_papers(filters, search, limit, offset)
        return {
            "papers": papers,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/stats")
def get_stats():
    """
    Returns statistics about the papers and the last update log.
    """
    try:
        return database.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Global state to track background update progress
is_updating = False

def run_update_task(log_id):
    global is_updating
    try:
        fetcher.fetch_and_update(log_id)
    except Exception as e:
        import traceback
        err_msg = f"Fatal error in background update task: {str(e)}\n{traceback.format_exc()}"
        try:
            database.update_update_log(log_id, "failed", 0, 0, 0, err_msg)
        except Exception as db_err:
            print(f"Error updating failed log: {db_err}")
    finally:
        is_updating = False

@app.post("/api/update")
def trigger_update(background_tasks: BackgroundTasks):
    """
    Triggers a manual database update in a background task.
    """
    global is_updating
    if is_updating:
        return {
            "status": "error",
            "message": "A database update is already in progress."
        }
        
    is_updating = True
    try:
        log_id = database.start_update_log()
        background_tasks.add_task(run_update_task, log_id)
        return {
            "status": "started",
            "message": "Publications update triggered in the background.",
            "log_id": log_id
        }
    except Exception as e:
        is_updating = False
        raise HTTPException(status_code=500, detail=f"Failed to start update: {str(e)}")

@app.get("/api/update/status")
def get_update_status():
    """
    Returns whether an update is running and details of the latest update log.
    """
    global is_updating
    try:
        stats = database.get_stats()
        return {
            "is_updating": is_updating,
            "last_update": stats.get('last_update')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Agent Curation Endpoints
@app.post("/api/papers/{paper_id}/curate")
def curate_paper(paper_id: int):
    """
    Triggers the multi-agent consensus panel for a specific paper.
    """
    paper = database.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
        
    try:
        review_data = agents_curator.curate_paper(paper)
        database.add_or_update_agent_review(review_data)
        return {
            "status": "success",
            "message": "Paper curated successfully",
            "review": review_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Curation error: {str(e)}")

@app.get("/api/papers/{paper_id}/review")
def get_paper_review(paper_id: int):
    """
    Retrieves the curated academic review for a specific paper.
    """
    paper = database.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
        
    try:
        review = database.get_agent_review(paper['doi'])
        if not review:
            return {
                "status": "pending",
                "message": "No review exists for this paper yet."
            }
        return {
            "status": "success",
            "review": review
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# HITL Triage Endpoints
@app.get("/api/triage")
def get_triage(
    status: str = Query("pending"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Returns papers pending triage review.
    """
    try:
        papers, total = database.get_triage_queue(status, limit, offset)
        return {
            "papers": papers,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/triage/{triage_id}/approve")
def approve_triage(triage_id: int):
    """
    Approves a paper in the triage queue and moves it to the main papers table.
    """
    try:
        success = database.approve_triage_paper(triage_id)
        if not success:
            raise HTTPException(status_code=404, detail="Triage paper not found or already processed")
        return {"status": "success", "message": "Paper approved and moved to main database"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Triage error: {str(e)}")

@app.post("/api/triage/{triage_id}/reject")
def reject_triage(triage_id: int):
    """
    Rejects a paper in the triage queue.
    """
    try:
        success = database.reject_triage_paper(triage_id)
        if not success:
            raise HTTPException(status_code=404, detail="Triage paper not found or already processed")
        return {"status": "success", "message": "Paper rejected from triage queue"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
# Grid Simulation Endpoints
@app.post("/api/simulate/power-flow")
def api_run_power_flow(data: dict):
    case_id = data.get("case_id")
    analysis_type = data.get("analysis_type")
    if not case_id or not analysis_type:
        raise HTTPException(status_code=400, detail="Missing case_id or analysis_type")
    
    import mcp_server
    res = mcp_server.tool_run_power_flow(case_id, analysis_type)
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    return res

@app.post("/api/simulate/solar-building")
def api_run_solar_building(data: dict):
    building_type = data.get("building_type")
    battery_cap = data.get("battery_cap", 5000.0)
    solar_cap = data.get("solar_cap", 1000.0)
    days = data.get("days", 1)
    if not building_type:
        raise HTTPException(status_code=400, detail="Missing building_type")
        
    import mcp_server
    res = mcp_server.tool_simulate_solar_building(building_type, battery_cap, solar_cap, days)
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
    return res

# Serve frontend files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "error",
        "message": "Frontend index.html not found. Place the file in the /static folder."
    }

# Mount static files for assets (CSS, JS)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
