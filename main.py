"""
EcoMind: Autonomous Environmental Intelligence System
Main application entry point
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

from agents.monitoring_agent import EnvironmentalMonitoringAgent
from agents.predictive_agent import PredictiveActionAgent
from agents.community_agent import CommunityCoordinationAgent
from agents.coach_agent import PersonalSustainabilityCoach
from core.agent_orchestrator import AgentOrchestrator
from api.routes import router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="EcoMind - Autonomous Environmental Intelligence",
    description="Multi-agent AI system for environmental monitoring and action",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router, prefix="/api")

# Global agent orchestrator
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize and start all AI agents"""
    global orchestrator
    
    # Initialize agents
    monitoring_agent = EnvironmentalMonitoringAgent()
    predictive_agent = PredictiveActionAgent()
    community_agent = CommunityCoordinationAgent()
    coach_agent = PersonalSustainabilityCoach()
    
    # Create orchestrator
    orchestrator = AgentOrchestrator([
        monitoring_agent,
        predictive_agent,
        community_agent,
        coach_agent
    ])
    
    # Start autonomous operations
    await orchestrator.start()
    print("🌍 EcoMind agents are now running autonomously!")

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown all agents"""
    global orchestrator
    if orchestrator:
        await orchestrator.stop()
    print("🛑 EcoMind agents stopped.")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application interface"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_running": orchestrator.is_running() if orchestrator else False,
        "version": "1.0.0"
    }

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    return await orchestrator.get_status()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
