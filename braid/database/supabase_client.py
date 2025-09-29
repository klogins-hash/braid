"""
Supabase client configuration for Braid AI agents.
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for Braid agents."""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        # Use service role key for admin operations, anon key for regular operations
        self.client: Client = create_client(self.url, self.service_role_key or self.anon_key)
        self.anon_client: Client = create_client(self.url, self.anon_key)
    
    async def create_agent_session(self, agent_id: str, session_data: Dict[str, Any]) -> str:
        """Create a new agent session."""
        try:
            result = self.client.table("agent_sessions").insert({
                "agent_id": agent_id,
                "session_data": session_data,
                "status": "active"
            }).execute()
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to create agent session: {e}")
            raise
    
    async def update_agent_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing agent session."""
        try:
            self.client.table("agent_sessions").update(updates).eq("id", session_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update agent session {session_id}: {e}")
            return False
    
    async def get_agent_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an agent session."""
        try:
            result = self.client.table("agent_sessions").select("*").eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get agent session {session_id}: {e}")
            return None
    
    async def store_agent_memory(self, agent_id: str, memory_type: str, content: Dict[str, Any]) -> str:
        """Store agent memory/state."""
        try:
            result = self.client.table("agent_memory").insert({
                "agent_id": agent_id,
                "memory_type": memory_type,
                "content": content
            }).execute()
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to store agent memory: {e}")
            raise
    
    async def get_agent_memory(self, agent_id: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve agent memory/state."""
        try:
            query = self.client.table("agent_memory").select("*").eq("agent_id", agent_id)
            if memory_type:
                query = query.eq("memory_type", memory_type)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get agent memory for {agent_id}: {e}")
            return []
    
    async def log_agent_action(self, agent_id: str, action: str, details: Dict[str, Any]) -> str:
        """Log agent actions for observability."""
        try:
            result = self.client.table("agent_logs").insert({
                "agent_id": agent_id,
                "action": action,
                "details": details,
                "timestamp": "now()"
            }).execute()
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to log agent action: {e}")
            raise
    
    async def get_integration_config(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get integration configuration."""
        try:
            result = self.client.table("integrations").select("*").eq("name", integration_name).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get integration config for {integration_name}: {e}")
            return None

# Global instance
supabase_client = SupabaseClient()
