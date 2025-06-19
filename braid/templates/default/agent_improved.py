#!/usr/bin/env python3
"""
Improved Braid Agent Template
Provides robust LangGraph state handling and error management.
"""

from typing import Annotated, Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Properly typed state for LangGraph with required fields."""
    messages: List[Dict[str, Any]]
    current_task: str
    status: str
    results: Dict[str, Any]
    error: Optional[str]
    metadata: Dict[str, Any]


class ImprovedBraidAgent:
    """Enhanced Braid agent with robust state management and error handling."""
    
    def __init__(self):
        """Initialize the agent with proper state management."""
        self.graph = self._create_graph()
        logger.info("Improved Braid agent initialized")
    
    def _create_graph(self) -> CompiledStateGraph:
        """Create the workflow graph with proper state handling."""
        
        # Define the workflow graph with typed state
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("initialize", self.initialize_task)
        workflow.add_node("process", self.process_task)
        workflow.add_node("finalize", self.finalize_task)
        workflow.add_node("error_handler", self.handle_error)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Define transitions with error handling
        workflow.add_conditional_edges(
            "initialize",
            self._should_continue_after_init,
            {
                "process": "process",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "process",
            self._should_continue_after_process,
            {
                "finalize": "finalize",
                "error": "error_handler"
            }
        )
        
        # Both finalize and error_handler end the workflow
        workflow.add_edge("finalize", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def initialize_task(self, state: AgentState) -> AgentState:
        """Initialize the task with proper error handling."""
        try:
            logger.info(f"Initializing task: {state.get('current_task', 'Unknown')}")
            
            # Update state with initialization
            state["status"] = "initialized"
            state["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "initialize",
                "details": "Task initialization completed"
            })
            
            # Clear any previous errors
            state["error"] = None
            
            return state
            
        except Exception as e:
            logger.error(f"Error in initialize_task: {e}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def process_task(self, state: AgentState) -> AgentState:
        """Process the main task logic."""
        try:
            logger.info("Processing main task logic")
            
            current_task = state.get("current_task", "")
            
            # Simulate task processing based on task type
            if "urgent" in current_task.lower():
                result = await self._handle_urgent_task(current_task)
            elif "analyze" in current_task.lower():
                result = await self._handle_analysis_task(current_task)
            else:
                result = await self._handle_general_task(current_task)
            
            # Update state with results
            state["results"].update(result)
            state["status"] = "processed"
            state["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "process",
                "details": f"Task processed successfully: {result.get('summary', 'Completed')}"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Error in process_task: {e}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def finalize_task(self, state: AgentState) -> AgentState:
        """Finalize the task and prepare final results."""
        try:
            logger.info("Finalizing task")
            
            # Prepare final summary
            final_summary = {
                "task": state.get("current_task"),
                "status": "completed",
                "results": state.get("results", {}),
                "message_count": len(state.get("messages", [])),
                "completed_at": datetime.now().isoformat()
            }
            
            state["results"]["final_summary"] = final_summary
            state["status"] = "completed"
            state["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "finalize",
                "details": "Task completed successfully"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Error in finalize_task: {e}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully."""
        logger.error(f"Handling error: {state.get('error', 'Unknown error')}")
        
        error_details = {
            "error_message": state.get("error", "Unknown error"),
            "failed_at": datetime.now().isoformat(),
            "task": state.get("current_task", "Unknown"),
            "partial_results": state.get("results", {})
        }
        
        state["results"]["error_details"] = error_details
        state["status"] = "failed"
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "error_handler",
            "details": f"Error handled: {error_details['error_message']}"
        })
        
        return state
    
    def _should_continue_after_init(self, state: AgentState) -> str:
        """Determine next step after initialization."""
        if state.get("error"):
            return "error"
        return "process"
    
    def _should_continue_after_process(self, state: AgentState) -> str:
        """Determine next step after processing."""
        if state.get("error"):
            return "error"
        return "finalize"
    
    async def _handle_urgent_task(self, task: str) -> Dict[str, Any]:
        """Handle urgent tasks with high priority."""
        logger.info("Handling urgent task")
        await asyncio.sleep(0.1)  # Simulate processing
        
        return {
            "type": "urgent",
            "priority": "high",
            "summary": "Urgent task processed with high priority",
            "actions_taken": ["immediate_notification", "escalation_triggered"]
        }
    
    async def _handle_analysis_task(self, task: str) -> Dict[str, Any]:
        """Handle analysis tasks with data processing."""
        logger.info("Handling analysis task")
        await asyncio.sleep(0.2)  # Simulate analysis
        
        return {
            "type": "analysis",
            "priority": "medium",
            "summary": "Analysis completed with insights generated",
            "insights": ["pattern_detected", "trend_identified"],
            "confidence": 0.85
        }
    
    async def _handle_general_task(self, task: str) -> Dict[str, Any]:
        """Handle general tasks with standard processing."""
        logger.info("Handling general task")
        await asyncio.sleep(0.1)  # Simulate processing
        
        return {
            "type": "general",
            "priority": "normal",
            "summary": "General task completed successfully",
            "actions_taken": ["standard_processing", "result_generated"]
        }
    
    async def execute_task(self, task_description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task with proper state management.
        
        Args:
            task_description: Description of the task to execute
            metadata: Optional metadata for the task
            
        Returns:
            Task execution results
        """
        logger.info(f"Executing task: {task_description}")
        
        # Initialize state with proper structure
        initial_state = AgentState(
            messages=[],
            current_task=task_description,
            status="pending",
            results={},
            error=None,
            metadata=metadata or {}
        )
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract results safely
            return {
                "success": final_state.get("status") == "completed",
                "status": final_state.get("status", "unknown"),
                "results": final_state.get("results", {}),
                "messages": final_state.get("messages", []),
                "error": final_state.get("error"),
                "task": task_description
            }
            
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "task": task_description,
                "results": {},
                "messages": []
            }


async def main():
    """Main function to demonstrate the improved agent."""
    logger.info("🚀 Starting Improved Braid Agent Demo")
    
    # Initialize agent
    agent = ImprovedBraidAgent()
    
    # Test scenarios
    test_tasks = [
        "Process urgent customer escalation for login issues",
        "Analyze customer satisfaction data from recent surveys",
        "Generate weekly support report for management",
        "Handle general inquiry about product features"
    ]
    
    results = []
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n📋 Task {i}: {task}")
        print("-" * 60)
        
        result = await agent.execute_task(
            task,
            metadata={"task_id": f"TASK-{i:03d}", "priority": "normal"}
        )
        
        print(f"✅ Status: {result['status']}")
        print(f"🎯 Success: {result['success']}")
        
        if result['success']:
            summary = result['results'].get('final_summary', {})
            print(f"📊 Results: {summary.get('status', 'Unknown')}")
            
            if 'type' in result['results']:
                print(f"🔧 Type: {result['results']['type']}")
                print(f"⚡ Priority: {result['results']['priority']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        results.append(result)
    
    # Summary
    successful_tasks = sum(1 for r in results if r['success'])
    print(f"\n🎉 Demo completed!")
    print(f"📈 Success rate: {successful_tasks}/{len(test_tasks)} ({successful_tasks/len(test_tasks)*100:.1f}%)")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())