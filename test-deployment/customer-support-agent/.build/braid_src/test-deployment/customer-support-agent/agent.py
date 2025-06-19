#!/usr/bin/env python3
"""
Customer Support Agent
Automated customer support with multi-channel communication, knowledge management, and data analytics.
"""

from typing import Annotated, Dict, Any, List, Optional
from langgraph.graph import StateGraph, Graph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from pydantic import BaseModel

import asyncio
import json
import csv
import requests
from datetime import datetime
from pathlib import Path


class CustomerSupportState(BaseModel):
    """State for customer support operations."""
    customer_id: Optional[str] = None
    issue_description: str = ""
    ticket_id: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    status: str = "open"  # open, in_progress, resolved, escalated
    messages: List[Dict[str, Any]] = []
    escalation_needed: bool = False
    solution: Optional[str] = None
    customer_data: Dict[str, Any] = {}


class CustomerSupportAgent:
    """Advanced customer support agent with MCP integration."""
    
    def __init__(self):
        """Initialize the customer support agent."""
        self.state = CustomerSupportState()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> CompiledStateGraph:
        """Create the customer support workflow graph."""
        
        # Define the workflow graph
        workflow = StateGraph(CustomerSupportState)
        
        # Add nodes for different support operations
        workflow.add_node("classify_issue", self.classify_issue)
        workflow.add_node("search_knowledge_base", self.search_knowledge_base)
        workflow.add_node("create_ticket", self.create_ticket)
        workflow.add_node("analyze_customer_data", self.analyze_customer_data)
        workflow.add_node("generate_solution", self.generate_solution)
        workflow.add_node("send_notification", self.send_notification)
        workflow.add_node("escalate_to_human", self.escalate_to_human)
        workflow.add_node("update_ticket", self.update_ticket)
        
        # Define the workflow flow
        workflow.set_entry_point("classify_issue")
        
        # Classification leads to knowledge search
        workflow.add_edge("classify_issue", "search_knowledge_base")
        
        # Search can lead to ticket creation or direct solution
        workflow.add_conditional_edges(
            "search_knowledge_base",
            self._should_create_ticket,
            {
                "create_ticket": "create_ticket",
                "analyze_data": "analyze_customer_data"
            }
        )
        
        # Ticket creation leads to data analysis
        workflow.add_edge("create_ticket", "analyze_customer_data")
        
        # Data analysis leads to solution generation
        workflow.add_edge("analyze_customer_data", "generate_solution")
        
        # Solution generation can lead to notification or escalation
        workflow.add_conditional_edges(
            "generate_solution",
            self._should_escalate,
            {
                "escalate": "escalate_to_human",
                "notify": "send_notification"
            }
        )
        
        # Both notification and escalation lead to ticket update
        workflow.add_edge("send_notification", "update_ticket")
        workflow.add_edge("escalate_to_human", "update_ticket")
        
        # Compile the graph
        return workflow.compile()
    
    async def classify_issue(self, state: CustomerSupportState) -> CustomerSupportState:
        """Classify the customer issue and determine priority."""
        print(f"🔍 Classifying issue: {state.issue_description}")
        
        # Issue classification logic
        issue_lower = state.issue_description.lower()
        
        if any(keyword in issue_lower for keyword in ["urgent", "critical", "down", "broken", "emergency"]):
            state.priority = "critical"
        elif any(keyword in issue_lower for keyword in ["billing", "payment", "charge", "refund"]):
            state.priority = "high"
        elif any(keyword in issue_lower for keyword in ["question", "how to", "help", "support"]):
            state.priority = "medium"
        else:
            state.priority = "low"
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "classify_issue",
            "details": f"Issue classified as {state.priority} priority"
        })
        
        print(f"✅ Issue classified as: {state.priority} priority")
        return state
    
    async def search_knowledge_base(self, state: CustomerSupportState) -> CustomerSupportState:
        """Search Notion knowledge base for existing solutions."""
        print("📚 Searching knowledge base in Notion...")
        
        # This would use the Notion MCP to search the knowledge base
        # For demo, we'll simulate the search
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "search_knowledge_base",
            "details": "Searched Notion knowledge base for similar issues"
        })
        
        # Simulate finding relevant knowledge base articles
        knowledge_results = [
            {
                "title": "Common Login Issues Resolution",
                "url": "https://notion.so/kb/login-issues",
                "relevance": 0.85
            },
            {
                "title": "Billing FAQ and Solutions", 
                "url": "https://notion.so/kb/billing-faq",
                "relevance": 0.72
            }
        ]
        
        state.customer_data["knowledge_base_results"] = knowledge_results
        print(f"✅ Found {len(knowledge_results)} relevant knowledge base articles")
        return state
    
    async def create_ticket(self, state: CustomerSupportState) -> CustomerSupportState:
        """Create a new support ticket in Notion."""
        print("🎫 Creating support ticket in Notion...")
        
        # Generate ticket ID
        state.ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # This would use the Notion MCP to create a ticket
        ticket_data = {
            "ticket_id": state.ticket_id,
            "customer_id": state.customer_id,
            "issue": state.issue_description,
            "priority": state.priority,
            "status": state.status,
            "created_at": datetime.now().isoformat()
        }
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "create_ticket",
            "details": f"Created ticket {state.ticket_id} in Notion database"
        })
        
        print(f"✅ Created ticket: {state.ticket_id}")
        return state
    
    async def analyze_customer_data(self, state: CustomerSupportState) -> CustomerSupportState:
        """Analyze customer data from CSV files and other sources."""
        print("📊 Analyzing customer data...")
        
        # Simulate customer data analysis from CSV
        customer_analysis = {
            "account_age_months": 12,
            "previous_tickets": 3,
            "satisfaction_score": 4.2,
            "subscription_tier": "premium",
            "last_interaction": "2024-01-15"
        }
        
        state.customer_data["analysis"] = customer_analysis
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "analyze_customer_data",
            "details": "Analyzed customer history and engagement data"
        })
        
        print("✅ Customer data analysis completed")
        return state
    
    async def generate_solution(self, state: CustomerSupportState) -> CustomerSupportState:
        """Generate a solution based on knowledge base and customer data."""
        print("💡 Generating solution...")
        
        # Solution generation logic based on issue type and customer data
        if state.priority == "critical":
            state.solution = "Immediate escalation to senior support with priority handling"
            state.escalation_needed = True
        elif "billing" in state.issue_description.lower():
            state.solution = "Review billing history and provide detailed breakdown"
        elif "login" in state.issue_description.lower():
            state.solution = "Password reset and account verification steps"
        else:
            state.solution = "Standard troubleshooting steps and knowledge base articles"
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "generate_solution",
            "details": f"Generated solution: {state.solution}"
        })
        
        print(f"✅ Generated solution: {state.solution}")
        return state
    
    async def send_notification(self, state: CustomerSupportState) -> CustomerSupportState:
        """Send SMS notification to customer via Twilio."""
        print("📱 Sending SMS notification via Twilio...")
        
        # This would use the Twilio MCP to send SMS
        notification_message = f"Hi! Your support ticket {state.ticket_id} has been created. We're working on: {state.solution}"
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "send_notification",
            "details": f"Sent SMS notification via Twilio: {notification_message[:50]}..."
        })
        
        print("✅ SMS notification sent")
        return state
    
    async def escalate_to_human(self, state: CustomerSupportState) -> CustomerSupportState:
        """Escalate issue to human agent via Slack."""
        print("🚨 Escalating to human agent via Slack...")
        
        state.status = "escalated"
        
        # This would use Slack integration to notify the team
        slack_message = f"🚨 ESCALATION: Ticket {state.ticket_id} needs immediate attention. Priority: {state.priority}. Issue: {state.issue_description}"
        
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "escalate_to_human",
            "details": "Escalated to human agent via Slack notification"
        })
        
        print("✅ Issue escalated to human agent")
        return state
    
    async def update_ticket(self, state: CustomerSupportState) -> CustomerSupportState:
        """Update the ticket status in Notion."""
        print("📝 Updating ticket status in Notion...")
        
        # This would use the Notion MCP to update the ticket
        state.messages.append({
            "timestamp": datetime.now().isoformat(),
            "action": "update_ticket",
            "details": f"Updated ticket {state.ticket_id} with status: {state.status}"
        })
        
        print(f"✅ Ticket {state.ticket_id} updated with status: {state.status}")
        return state
    
    def _should_create_ticket(self, state: CustomerSupportState) -> str:
        """Determine if a ticket should be created."""
        # Always create ticket for this demo
        return "create_ticket"
    
    def _should_escalate(self, state: CustomerSupportState) -> str:
        """Determine if issue should be escalated."""
        if state.escalation_needed or state.priority == "critical":
            return "escalate"
        else:
            return "notify"
    
    async def handle_support_request(self, customer_id: str, issue_description: str) -> Dict[str, Any]:
        """Handle a complete customer support request."""
        print(f"\n🎯 Processing support request for customer: {customer_id}")
        print(f"📋 Issue: {issue_description}")
        print("-" * 80)
        
        # Initialize state
        self.state = CustomerSupportState(
            customer_id=customer_id,
            issue_description=issue_description
        )
        
        # Run the workflow
        final_state = await self.graph.ainvoke(self.state)
        
        print("-" * 80)
        print("✅ Support request processing completed!")
        
        return {
            "ticket_id": final_state.get("ticket_id"),
            "status": final_state.get("status"),
            "priority": final_state.get("priority"),
            "solution": final_state.get("solution"),
            "messages": final_state.get("messages", [])
        }


# Native tools for file processing and HTTP requests
class NativeTools:
    """Native tools for data processing and API calls."""
    
    @staticmethod
    def process_csv_file(file_path: str) -> Dict[str, Any]:
        """Process CSV file and return analytics."""
        print(f"📄 Processing CSV file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            analytics = {
                "total_rows": len(data),
                "columns": list(data[0].keys()) if data else [],
                "sample_data": data[:5] if data else []
            }
            
            print(f"✅ Processed {analytics['total_rows']} rows")
            return analytics
            
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def make_http_request(url: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to external API."""
        print(f"🌐 Making {method} request to: {url}")
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data)
            else:
                response = requests.get(url)
            
            result = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
            
            print(f"✅ Request completed: {response.status_code}")
            return result
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}


async def main():
    """Main function to demonstrate the customer support agent."""
    print("🚀 Customer Support Agent Demo")
    print("=" * 80)
    
    # Initialize agent
    agent = CustomerSupportAgent()
    
    # Demo scenarios
    scenarios = [
        {
            "customer_id": "CUST-001",
            "issue": "I can't log into my account and it's urgent - I need to access my files for a meeting"
        },
        {
            "customer_id": "CUST-002", 
            "issue": "I was charged twice for my subscription this month"
        },
        {
            "customer_id": "CUST-003",
            "issue": "How do I export my data to CSV format?"
        }
    ]
    
    # Process each scenario
    results = []
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📞 SCENARIO {i}")
        result = await agent.handle_support_request(
            scenario["customer_id"],
            scenario["issue"]
        )
        results.append(result)
        
        print(f"🎫 Result: Ticket {result['ticket_id']} - Status: {result['status']}")
    
    # Demo native tools
    print(f"\n🛠️ NATIVE TOOLS DEMO")
    print("-" * 40)
    
    # Create sample CSV for testing
    sample_csv_path = "sample_customer_data.csv"
    with open(sample_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['customer_id', 'satisfaction', 'tickets'])
        writer.writeheader()
        writer.writerows([
            {'customer_id': 'CUST-001', 'satisfaction': 4.5, 'tickets': 2},
            {'customer_id': 'CUST-002', 'satisfaction': 3.8, 'tickets': 5},
            {'customer_id': 'CUST-003', 'satisfaction': 4.9, 'tickets': 1}
        ])
    
    # Test native tools
    tools = NativeTools()
    csv_result = tools.process_csv_file(sample_csv_path)
    print(f"CSV Analytics: {csv_result}")
    
    # Test HTTP request
    http_result = tools.make_http_request("https://httpbin.org/get")
    print(f"HTTP Request result: Status {http_result.get('status_code', 'N/A')}")
    
    print(f"\n🎉 Demo completed! Processed {len(results)} support requests")
    return results


if __name__ == "__main__":
    asyncio.run(main())