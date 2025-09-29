"""
Braid AI Agent System - Railway Web Server
"""
import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

from braid.database.supabase_client import supabase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Braid AI Agent System",
    description="Production-ready AI agents with LangGraph and 40+ integrations",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AgentRequest(BaseModel):
    agent_type: str
    config: Dict[str, Any] = {}
    tools: list = []

class AgentResponse(BaseModel):
    agent_id: str
    status: str
    message: str

class WorkflowRequest(BaseModel):
    agent_id: str
    workflow_name: str
    input_data: Dict[str, Any] = {}

class WorkflowResponse(BaseModel):
    execution_id: str
    status: str
    output_data: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Braid AI Agent System",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    try:
        # Test database connection
        await supabase_client.client.table("agents").select("count").execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "now()"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/agents", response_model=AgentResponse)
async def create_agent(request: AgentRequest):
    """Create a new AI agent."""
    try:
        # Set default LLM config if not provided
        default_config = {
            "llm_provider": "anthropic",
            "model": "claude-4-sonnet-20250101",  # Latest Claude 4 model
            **request.config
        }
        
        # Create agent in database
        result = supabase_client.client.table("agents").insert({
            "name": f"{request.agent_type}_agent",
            "description": f"AI agent of type {request.agent_type}",
            "config": default_config,
            "tools": request.tools
        }).execute()
        
        agent_id = result.data[0]["id"]
        
        # Log agent creation
        await supabase_client.log_agent_action(
            agent_id=str(agent_id),
            action="agent_created",
            details={"agent_type": request.agent_type, "config": request.config}
        )
        
        return AgentResponse(
            agent_id=str(agent_id),
            status="created",
            message=f"Agent {request.agent_type} created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    try:
        result = supabase_client.client.table("agents").select("*").eq("id", agent_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Agent not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_id}/workflows", response_model=WorkflowResponse)
async def execute_workflow(agent_id: str, request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Execute a workflow for an agent."""
    try:
        # Create workflow execution record
        result = supabase_client.client.table("workflow_executions").insert({
            "agent_id": agent_id,
            "workflow_name": request.workflow_name,
            "input_data": request.input_data,
            "status": "running"
        }).execute()
        
        execution_id = result.data[0]["id"]
        
        # Add background task to actually execute the workflow
        background_tasks.add_task(
            execute_workflow_background,
            execution_id,
            agent_id,
            request.workflow_name,
            request.input_data
        )
        
        return WorkflowResponse(
            execution_id=str(execution_id),
            status="running"
        )
    except Exception as e:
        logger.error(f"Failed to start workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/{execution_id}")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status."""
    try:
        result = supabase_client.client.table("workflow_executions").select("*").eq("id", execution_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status {execution_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/memory")
async def get_agent_memory(agent_id: str, memory_type: Optional[str] = None):
    """Get agent memory/state."""
    try:
        memory = await supabase_client.get_agent_memory(agent_id, memory_type)
        return {"agent_id": agent_id, "memory": memory}
    except Exception as e:
        logger.error(f"Failed to get agent memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/logs")
async def get_agent_logs(agent_id: str, limit: int = 100):
    """Get agent action logs."""
    try:
        result = supabase_client.client.table("agent_logs").select("*").eq("agent_id", agent_id).order("timestamp", desc=True).limit(limit).execute()
        return {"agent_id": agent_id, "logs": result.data}
    except Exception as e:
        logger.error(f"Failed to get agent logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_workflow_background(execution_id: str, agent_id: str, workflow_name: str, input_data: Dict[str, Any]):
    """Background task to execute workflow."""
    try:
        # This is where you'd integrate with LangGraph to actually execute the workflow
        # For now, we'll simulate a workflow execution
        await asyncio.sleep(2)  # Simulate processing time
        
        # Update execution status
        supabase_client.client.table("workflow_executions").update({
            "status": "completed",
            "output_data": {"result": "Workflow completed successfully", "input": input_data},
            "completed_at": "now()"
        }).eq("id", execution_id).execute()
        
        # Log completion
        await supabase_client.log_agent_action(
            agent_id=agent_id,
            action="workflow_completed",
            details={"workflow_name": workflow_name, "execution_id": execution_id}
        )
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        # Update execution status to failed
        supabase_client.client.table("workflow_executions").update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": "now()"
        }).eq("id", execution_id).execute()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "braid.server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
