"""
Template improvements for better agent development experience.
"""

def generate_improved_agent_template(agent_name: str, description: str, mcps: list = None) -> str:
    """Generate an improved agent template with robust error handling."""
    
    mcps = mcps or []
    mcp_imports = ""
    mcp_usage_examples = ""
    
    if mcps:
        mcp_imports = "\n# MCP Integration imports would go here"
        mcp_usage_examples = f"""
        # Example MCP usage for: {', '.join(mcps)}
        # These would be replaced with actual MCP tool calls
        """
    
    template = f'''#!/usr/bin/env python3
"""
{agent_name}
{description}

This agent template includes robust error handling and proper LangGraph state management.
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
import asyncio
import logging
from datetime import datetime
{mcp_imports}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Properly typed state for LangGraph operations."""
    messages: List[Dict[str, Any]]
    current_task: str
    status: str
    results: Dict[str, Any]
    error: Optional[str]
    metadata: Dict[str, Any]


class {agent_name.replace('-', '').replace('_', '').title()}Agent:
    """
    {description}
    
    Features:
    - Robust error handling and recovery
    - Proper LangGraph state management  
    - Comprehensive logging
    - Modular workflow design
    """
    
    def __init__(self):
        """Initialize the agent with proper configuration."""
        self.graph = self._create_graph()
        logger.info(f"{agent_name} agent initialized")
    
    def _create_graph(self) -> CompiledStateGraph:
        """Create the workflow graph with proper error handling."""
        
        workflow = StateGraph(AgentState)
        
        # Add workflow nodes
        workflow.add_node("initialize", self.initialize_task)
        workflow.add_node("process", self.process_task)
        workflow.add_node("finalize", self.finalize_task)
        workflow.add_node("error_handler", self.handle_error)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Define conditional transitions
        workflow.add_conditional_edges(
            "initialize",
            self._route_after_init,
            {{"process": "process", "error": "error_handler"}}
        )
        
        workflow.add_conditional_edges(
            "process", 
            self._route_after_process,
            {{"finalize": "finalize", "error": "error_handler"}}
        )
        
        # End states
        workflow.add_edge("finalize", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def initialize_task(self, state: AgentState) -> AgentState:
        """Initialize task processing with validation."""
        try:
            logger.info(f"Initializing: {{state.get('current_task', 'Unknown')}}")
            
            # Validate input
            if not state.get("current_task"):
                raise ValueError("No task provided for processing")
            
            # Update state
            state["status"] = "initialized"
            state["messages"].append({{
                "timestamp": datetime.now().isoformat(),
                "action": "initialize",
                "details": "Task initialization completed successfully"
            }})
            state["error"] = None
            
            return state
            
        except Exception as e:
            logger.error(f"Initialization failed: {{e}}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def process_task(self, state: AgentState) -> AgentState:
        """Main task processing logic."""
        try:
            logger.info("Processing main task logic")
            
            current_task = state.get("current_task", "")
            
            # Task processing logic here
            # Replace with your specific business logic
            result = await self._execute_task_logic(current_task)
            {mcp_usage_examples}
            
            # Update state with results
            state["results"].update(result)
            state["status"] = "processed"
            state["messages"].append({{
                "timestamp": datetime.now().isoformat(),
                "action": "process",
                "details": f"Task processed: {{result.get('summary', 'Completed')}}"
            }})
            
            return state
            
        except Exception as e:
            logger.error(f"Processing failed: {{e}}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def finalize_task(self, state: AgentState) -> AgentState:
        """Finalize task and prepare results."""
        try:
            logger.info("Finalizing task")
            
            # Prepare final summary
            final_summary = {{
                "task": state.get("current_task"),
                "status": "completed",
                "results": state.get("results", {{}}),
                "message_count": len(state.get("messages", [])),
                "completed_at": datetime.now().isoformat()
            }}
            
            state["results"]["final_summary"] = final_summary
            state["status"] = "completed"
            state["messages"].append({{
                "timestamp": datetime.now().isoformat(),
                "action": "finalize", 
                "details": "Task completed successfully"
            }})
            
            return state
            
        except Exception as e:
            logger.error(f"Finalization failed: {{e}}")
            state["error"] = str(e)
            state["status"] = "error"
            return state
    
    async def handle_error(self, state: AgentState) -> AgentState:
        """Handle errors gracefully with detailed logging."""
        error_msg = state.get("error", "Unknown error")
        logger.error(f"Handling error: {{error_msg}}")
        
        error_details = {{
            "error_message": error_msg,
            "failed_at": datetime.now().isoformat(),
            "task": state.get("current_task", "Unknown"),
            "partial_results": state.get("results", {{}})
        }}
        
        state["results"]["error_details"] = error_details
        state["status"] = "failed"
        state["messages"].append({{
            "timestamp": datetime.now().isoformat(),
            "action": "error_handler",
            "details": f"Error handled: {{error_msg}}"
        }})
        
        return state
    
    def _route_after_init(self, state: AgentState) -> str:
        """Route after initialization based on state."""
        return "error" if state.get("error") else "process"
    
    def _route_after_process(self, state: AgentState) -> str:
        """Route after processing based on state.""" 
        return "error" if state.get("error") else "finalize"
    
    async def _execute_task_logic(self, task: str) -> Dict[str, Any]:
        """
        Execute the main task logic.
        Replace this method with your specific business logic.
        """
        logger.info(f"Executing task logic for: {{task}}")
        
        # Simulate task processing
        await asyncio.sleep(0.1)
        
        # Example result - replace with actual logic
        return {{
            "type": "example",
            "summary": f"Processed task: {{task}}",
            "actions_taken": ["analysis", "processing", "result_generation"],
            "confidence": 0.95
        }}
    
    async def execute_task(self, task_description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task with comprehensive error handling.
        
        Args:
            task_description: Description of the task to execute
            metadata: Optional metadata for the task
            
        Returns:
            Task execution results with success status
        """
        logger.info(f"Executing task: {{task_description}}")
        
        # Initialize state
        initial_state = AgentState(
            messages=[],
            current_task=task_description,
            status="pending",
            results={{}},
            error=None,
            metadata=metadata or {{}}
        )
        
        try:
            # Execute workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Return structured results
            return {{
                "success": final_state.get("status") == "completed",
                "status": final_state.get("status", "unknown"),
                "results": final_state.get("results", {{}}),
                "messages": final_state.get("messages", []),
                "error": final_state.get("error"),
                "task": task_description
            }}
            
        except Exception as e:
            logger.error(f"Graph execution failed: {{e}}")
            return {{
                "success": False,
                "status": "failed",
                "error": str(e),
                "task": task_description,
                "results": {{}},
                "messages": []
            }}


async def main():
    """Main function for testing the agent."""
    print(f"🚀 Starting {{agent_name}} Demo")
    print("=" * 80)
    
    # Initialize agent
    agent = {agent_name.replace('-', '').replace('_', '').title()}Agent()
    
    # Example tasks
    test_tasks = [
        "Process customer inquiry about product features",
        "Analyze recent user feedback for insights", 
        "Generate summary report for management"
    ]
    
    results = []
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\\n📋 Task {{i}}: {{task}}")
        print("-" * 60)
        
        result = await agent.execute_task(
            task,
            metadata={{"task_id": f"TASK-{{i:03d}}", "priority": "normal"}}
        )
        
        print(f"✅ Status: {{result['status']}}")
        print(f"🎯 Success: {{result['success']}}")
        
        if result['success']:
            summary = result['results'].get('final_summary', {{}})
            print(f"📊 Result: {{summary.get('status', 'Unknown')}}")
        else:
            print(f"❌ Error: {{result.get('error', 'Unknown error')}}")
        
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\\n🎉 Demo completed!")
    print(f"📈 Success rate: {{successful}}/{{len(test_tasks)}} ({{successful/len(test_tasks)*100:.1f}}%)")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return template