"""
LibreChat adapter for Braid AI Agent System
Provides OpenAI-compatible API endpoints for LibreChat integration
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, AsyncGenerator
import json
import uuid
import time
from datetime import datetime

router = APIRouter(prefix="/v1", tags=["LibreChat"])

# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 4000
    stream: Optional[bool] = False
    user: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "braid-ai"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

@router.get("/models")
async def list_models():
    """List available Braid AI models in OpenAI format."""
    models = [
        {
            "id": "claude-4-sonnet-20250101",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "braid-ai"
        },
        {
            "id": "claude-4-opus-20250101", 
            "object": "model",
            "created": int(time.time()),
            "owned_by": "braid-ai"
        },
        {
            "id": "claude-4-haiku-20250101",
            "object": "model", 
            "created": int(time.time()),
            "owned_by": "braid-ai"
        }
    ]
    
    return ModelsResponse(data=models)

@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest, http_request: Request):
    """OpenAI-compatible chat completions endpoint for LibreChat."""
    try:
        from braid.database.supabase_client import supabase_client
        
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1].content
        
        # Create a Braid agent for this conversation
        agent_data = {
            "agent_type": "chat",
            "config": {
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            },
            "tools": []
        }
        
        # Create agent in database
        agent_result = supabase_client.client.table("agents").insert(agent_data).execute()
        agent_id = agent_result.data[0]["id"]
        
        # Execute chat workflow
        workflow_data = {
            "agent_id": str(agent_id),
            "workflow_name": "librechat_chat",
            "input_data": {
                "messages": [msg.dict() for msg in request.messages],
                "user_id": request.user or "librechat_user",
                "session_id": str(uuid.uuid4())
            }
        }
        
        workflow_result = supabase_client.client.table("workflow_executions").insert(workflow_data).execute()
        execution_id = workflow_result.data[0]["id"]
        
        # For now, return a mock response since we don't have the actual AI integration yet
        # In production, this would call the actual Claude API through Braid
        response_content = f"Hello! I'm a Braid AI agent using {request.model}. I received your message: '{last_message}'. This is a test response from the LibreChat integration. Once you add your Anthropic API key, I'll provide real AI responses!"
        
        # Log the interaction
        await supabase_client.log_agent_action(
            agent_id=str(agent_id),
            action="librechat_chat",
            details={
                "model": request.model,
                "message_count": len(request.messages),
                "execution_id": str(execution_id)
            }
        )
        
        # Return OpenAI-compatible response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=response_content),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": sum(len(msg.content.split()) for msg in request.messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": sum(len(msg.content.split()) for msg in request.messages) + len(response_content.split())
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")

@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get specific model information."""
    if model_id not in ["claude-4-sonnet-20250101", "claude-4-opus-20250101", "claude-4-haiku-20250101"]:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return ModelInfo(
        id=model_id,
        created=int(time.time()),
        owned_by="braid-ai"
    )

@router.post("/embeddings")
async def create_embeddings(request: Dict[str, Any]):
    """Embeddings endpoint (placeholder for future implementation)."""
    raise HTTPException(status_code=501, detail="Embeddings not yet implemented")

@router.post("/audio/transcriptions")
async def transcribe_audio(request: Dict[str, Any]):
    """Audio transcription endpoint (placeholder for future implementation)."""
    raise HTTPException(status_code=501, detail="Audio transcription not yet implemented")

@router.post("/audio/speech")
async def text_to_speech(request: Dict[str, Any]):
    """Text-to-speech endpoint (placeholder for future implementation)."""
    raise HTTPException(status_code=501, detail="Text-to-speech not yet implemented")
