"""
Knowledge base and RAG tools for the Onboarding & Internal Knowledge Expert agent.
Handles document search, retrieval, and service request routing.
"""
import os
import json
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="Search query for the knowledge base")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    include_sources: bool = Field(default=True, description="Include source document URLs")
    category_filter: Optional[str] = Field(
        default=None, 
        description="Filter by category: 'policy', 'process', 'technical', 'hr', 'legal'"
    )

class DocumentContextInput(BaseModel):
    document_id: str = Field(description="Document ID or URL to retrieve")
    include_related: bool = Field(default=True, description="Include related documents")

class ServiceRequestInput(BaseModel):
    request_type: str = Field(description="Type of service request")
    user_id: str = Field(description="Slack user ID making the request")
    description: str = Field(description="Description of what the user needs")
    urgency: str = Field(default="normal", description="Urgency level: 'low', 'normal', 'high', 'urgent'")

# --- Knowledge Base Simulation ---
# In production, this would be a vector database with real embeddings

KNOWLEDGE_BASE = {
    "policies": {
        "expense_reports": {
            "title": "Expense Report Submission Process",
            "content": "To submit an expense report: 1) Log into Concur, 2) Upload receipts, 3) Fill out expense form, 4) Submit for manager approval. Reports must be submitted within 30 days.",
            "source_url": "https://company.notion.so/Expense-Reports-abc123",
            "last_updated": "2024-01-15",
            "category": "policy",
            "keywords": ["expense", "receipts", "reimbursement", "concur", "travel"]
        },
        "remote_work": {
            "title": "Remote Work Policy",
            "content": "Employees may work remotely up to 3 days per week with manager approval. Core hours are 10 AM - 4 PM EST. Home office stipend available up to $500/year.",
            "source_url": "https://company.notion.so/Remote-Work-Policy-def456",
            "last_updated": "2024-02-01",
            "category": "policy",
            "keywords": ["remote", "work from home", "wfh", "hybrid", "stipend"]
        },
        "pto_policy": {
            "title": "Paid Time Off (PTO) Policy",
            "content": "Unlimited PTO policy with minimum 2 weeks encouraged per year. Request time off through BambooHR at least 2 weeks in advance for extended leave.",
            "source_url": "https://company.notion.so/PTO-Policy-ghi789",
            "last_updated": "2024-01-20",
            "category": "policy",
            "keywords": ["pto", "vacation", "time off", "bamboohr", "leave"]
        }
    },
    "processes": {
        "code_review": {
            "title": "Code Review Process",
            "content": "All code must be reviewed before merging. Create PR, assign 2 reviewers, run CI tests. Use conventional commits. Merge only after approval and passing tests.",
            "source_url": "https://company.notion.so/Code-Review-Process-jkl012",
            "last_updated": "2024-01-10",
            "category": "process",
            "keywords": ["code review", "pr", "pull request", "merge", "ci", "testing"]
        },
        "incident_response": {
            "title": "Incident Response Procedure",
            "content": "For production incidents: 1) Alert #incidents channel, 2) Create incident doc, 3) Form response team, 4) Communicate updates, 5) Post-mortem within 48 hours.",
            "source_url": "https://company.notion.so/Incident-Response-mno345",
            "last_updated": "2024-01-25",
            "category": "process",
            "keywords": ["incident", "outage", "production", "postmortem", "alert"]
        },
        "release_process": {
            "title": "Software Release Process",
            "content": "Weekly releases every Tuesday. Feature freeze Monday EOD. Deploy to staging, run QA tests, deploy to production with rollback plan ready.",
            "source_url": "https://company.notion.so/Release-Process-pqr678",
            "last_updated": "2024-02-05",
            "category": "process",
            "keywords": ["release", "deploy", "staging", "production", "qa", "rollback"]
        }
    },
    "technical": {
        "vpn_access": {
            "title": "VPN Setup and Access",
            "content": "Download FortiClient VPN. Use credentials from IT. Connect to vpn.company.com. For issues, contact IT support at it-help@company.com or #it-support channel.",
            "source_url": "https://company.notion.so/VPN-Setup-stu901",
            "last_updated": "2024-01-30",
            "category": "technical",
            "keywords": ["vpn", "forticlient", "network", "access", "it support"]
        },
        "aws_access": {
            "title": "AWS Account Access",
            "content": "Request AWS access through IT ticket. Use SSO login at company.awsapps.com. Follow principle of least privilege. MFA required for all accounts.",
            "source_url": "https://company.notion.so/AWS-Access-vwx234",
            "last_updated": "2024-02-10",
            "category": "technical",
            "keywords": ["aws", "cloud", "sso", "mfa", "access", "permissions"]
        },
        "database_access": {
            "title": "Database Access Procedures",
            "content": "Production DB access requires approval. Use read-only replica for queries. Emergency access through on-call engineer. All queries logged and audited.",
            "source_url": "https://company.notion.so/Database-Access-yz567",
            "last_updated": "2024-01-18",
            "category": "technical",
            "keywords": ["database", "production", "sql", "replica", "audit"]
        }
    },
    "contacts": {
        "product_managers": {
            "title": "Product Management Team",
            "content": "Product Alpha: Sarah Chen (@sarah.chen), Product Beta: Mike Rodriguez (@mike.rodriguez), Platform: Lisa Wang (@lisa.wang)",
            "source_url": "https://company.notion.so/Product-Team-abc890",
            "last_updated": "2024-02-01",
            "category": "contact",
            "keywords": ["product manager", "pm", "product", "sarah chen", "mike rodriguez", "lisa wang"]
        },
        "engineering_leads": {
            "title": "Engineering Leadership",
            "content": "VP Engineering: David Kim (@david.kim), Backend Lead: Jessica Liu (@jessica.liu), Frontend Lead: Tom Wilson (@tom.wilson), DevOps Lead: Alex Brown (@alex.brown)",
            "source_url": "https://company.notion.so/Engineering-Leads-def123",
            "last_updated": "2024-01-15",
            "category": "contact",
            "keywords": ["engineering", "lead", "vp", "backend", "frontend", "devops"]
        }
    },
    "forms": {
        "it_requests": {
            "title": "IT Support Request Form",
            "content": "Submit IT requests through ServiceNow portal at company.service-now.com. For urgent issues, ping #it-support or call ext. 911.",
            "source_url": "https://company.service-now.com/it-request",
            "last_updated": "2024-02-01",
            "category": "service",
            "keywords": ["it request", "servicenow", "support", "hardware", "software", "access"]
        },
        "software_licenses": {
            "title": "Software License Requests",
            "content": "Request software licenses through IT portal. Common tools: Figma, Slack Premium, JetBrains, Adobe Creative. Include business justification.",
            "source_url": "https://company.notion.so/Software-Licenses-ghi456",
            "last_updated": "2024-01-20",
            "category": "service",
            "keywords": ["software", "license", "figma", "adobe", "jetbrains", "tools"]
        }
    }
}

# --- Helper Functions ---

def search_knowledge_documents(query: str, category_filter: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search through the knowledge base using keyword matching."""
    query_lower = query.lower()
    results = []
    
    for category, documents in KNOWLEDGE_BASE.items():
        # Apply category filter if specified
        if category_filter and category != category_filter:
            continue
            
        for doc_id, doc_data in documents.items():
            # Calculate relevance score based on keyword matches
            score = 0
            keywords = doc_data.get("keywords", [])
            
            # Check title match
            if any(word in doc_data["title"].lower() for word in query_lower.split()):
                score += 3
            
            # Check content match
            if any(word in doc_data["content"].lower() for word in query_lower.split()):
                score += 2
                
            # Check keyword match
            if any(keyword in query_lower for keyword in keywords):
                score += 1
            
            # Check exact keyword match
            if any(query_lower in keyword for keyword in keywords):
                score += 2
            
            if score > 0:
                result = {
                    "document_id": doc_id,
                    "title": doc_data["title"],
                    "content": doc_data["content"],
                    "source_url": doc_data["source_url"],
                    "category": doc_data["category"],
                    "last_updated": doc_data["last_updated"],
                    "relevance_score": score
                }
                results.append(result)
    
    # Sort by relevance score and return top results
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:max_results]

def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific document by ID."""
    for category, documents in KNOWLEDGE_BASE.items():
        if document_id in documents:
            doc_data = documents[document_id]
            return {
                "document_id": document_id,
                "title": doc_data["title"],
                "content": doc_data["content"],
                "source_url": doc_data["source_url"],
                "category": doc_data["category"],
                "last_updated": doc_data["last_updated"]
            }
    return None

# --- Tool Implementations ---

@tool("search_knowledge_base", args_schema=KnowledgeSearchInput)
def search_knowledge_base(
    query: str,
    max_results: int = 5,
    include_sources: bool = True,
    category_filter: Optional[str] = None
) -> str:
    """
    Search the company knowledge base for relevant information.
    
    This tool performs semantic search across all company documentation,
    policies, processes, and technical guides to find relevant answers.
    """
    try:
        # Perform the search
        results = search_knowledge_documents(query, category_filter, max_results)
        
        if not results:
            return json.dumps({
                "success": False,
                "message": "No relevant documents found for your query",
                "query": query,
                "suggestions": [
                    "Try using different keywords",
                    "Check for typos in your query", 
                    "Ask a more specific question",
                    "Contact #general for help if this is urgent"
                ]
            })
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "title": result["title"],
                "summary": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "category": result["category"],
                "relevance_score": result["relevance_score"]
            }
            
            if include_sources:
                formatted_result["source_url"] = result["source_url"]
                formatted_result["last_updated"] = result["last_updated"]
            
            formatted_results.append(formatted_result)
        
        return json.dumps({
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": formatted_results,
            "search_metadata": {
                "category_filter": category_filter,
                "max_results": max_results,
                "search_time": "< 1 second"
            }
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error searching knowledge base: {str(e)}"
        })

@tool("get_document_with_context", args_schema=DocumentContextInput)
def get_document_with_context(
    document_id: str,
    include_related: bool = True
) -> str:
    """
    Retrieve a specific document with full content and related information.
    
    Provides complete document content plus suggestions for related documents
    that might be helpful.
    """
    try:
        # Get the main document
        document = get_document_by_id(document_id)
        
        if not document:
            return json.dumps({
                "success": False,
                "message": f"Document '{document_id}' not found",
                "available_categories": list(KNOWLEDGE_BASE.keys())
            })
        
        response = {
            "success": True,
            "document": document
        }
        
        # Find related documents if requested
        if include_related:
            # Use document keywords to find related content
            doc_data = None
            for category, documents in KNOWLEDGE_BASE.items():
                if document_id in documents:
                    doc_data = documents[document_id]
                    break
            
            if doc_data:
                keywords = doc_data.get("keywords", [])
                related_docs = []
                
                for category, documents in KNOWLEDGE_BASE.items():
                    for other_id, other_data in documents.items():
                        if other_id != document_id:
                            # Check for keyword overlap
                            other_keywords = other_data.get("keywords", [])
                            overlap = set(keywords) & set(other_keywords)
                            
                            if overlap:
                                related_docs.append({
                                    "document_id": other_id,
                                    "title": other_data["title"],
                                    "category": other_data["category"],
                                    "source_url": other_data["source_url"],
                                    "shared_keywords": list(overlap)
                                })
                
                # Sort by number of shared keywords and return top 3
                related_docs.sort(key=lambda x: len(x["shared_keywords"]), reverse=True)
                response["related_documents"] = related_docs[:3]
        
        return json.dumps(response)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error retrieving document: {str(e)}"
        })

@tool("create_service_request", args_schema=ServiceRequestInput)
def create_service_request(
    request_type: str,
    user_id: str,
    description: str,
    urgency: str = "normal"
) -> str:
    """
    Create a service request or route user to appropriate request form.
    
    Handles common IT requests, software licenses, access requests, and
    provides direct links to forms or escalation paths.
    """
    try:
        # Define service request routing
        service_routes = {
            "it_support": {
                "form_url": "https://company.service-now.com/it-request",
                "slack_channel": "#it-support",
                "description": "Hardware, software, and technical support requests"
            },
            "software_license": {
                "form_url": "https://company.notion.so/Software-License-Request",
                "slack_channel": "#it-support",
                "description": "Figma, Adobe, JetBrains, and other software licenses"
            },
            "access_request": {
                "form_url": "https://company.service-now.com/access-request",
                "slack_channel": "#security",
                "description": "AWS, database, VPN, and system access requests"
            },
            "hr_request": {
                "form_url": "https://company.bamboohr.com/requests",
                "slack_channel": "#people-ops",
                "description": "Benefits, PTO, and HR-related requests"
            },
            "facilities": {
                "form_url": "https://company.notion.so/Facilities-Request",
                "slack_channel": "#facilities",
                "description": "Office supplies, room bookings, and facilities issues"
            }
        }
        
        # Auto-detect request type based on description if not specified
        description_lower = description.lower()
        if request_type == "auto":
            if any(word in description_lower for word in ["figma", "adobe", "license", "software"]):
                request_type = "software_license"
            elif any(word in description_lower for word in ["access", "aws", "database", "vpn"]):
                request_type = "access_request"
            elif any(word in description_lower for word in ["pto", "benefits", "hr", "time off"]):
                request_type = "hr_request"
            elif any(word in description_lower for word in ["office", "supplies", "room", "facilities"]):
                request_type = "facilities"
            else:
                request_type = "it_support"
        
        # Get routing information
        if request_type not in service_routes:
            return json.dumps({
                "success": False,
                "message": f"Unknown request type: {request_type}",
                "available_types": list(service_routes.keys()),
                "general_help": "For general questions, try asking in #general or contact your manager"
            })
        
        route_info = service_routes[request_type]
        
        # Generate appropriate response based on urgency
        if urgency == "urgent":
            response = {
                "success": True,
                "message": "Urgent request detected - providing immediate escalation paths",
                "request_type": request_type,
                "immediate_action": f"Post in {route_info['slack_channel']} with @here for immediate attention",
                "form_url": route_info["form_url"],
                "follow_up": "Also submit the form for proper tracking",
                "escalation": "If no response in 30 minutes, contact your manager or #leadership"
            }
        else:
            response = {
                "success": True,
                "message": f"Service request routing for: {request_type}",
                "request_type": request_type,
                "description": route_info["description"],
                "recommended_action": f"Submit request form: {route_info['form_url']}",
                "alternative": f"For quick questions, ask in {route_info['slack_channel']}",
                "urgency": urgency,
                "estimated_response": "1-2 business days for normal requests"
            }
        
        # Add user context
        response["user_id"] = user_id
        response["request_description"] = description
        response["submitted_at"] = json.dumps({"timestamp": "2024-01-01T00:00:00Z"})  # Placeholder
        
        return json.dumps(response)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error creating service request: {str(e)}"
        })

@tool("get_quick_answers")
def get_quick_answers(query: str) -> str:
    """
    Get quick answers to common questions without full knowledge base search.
    
    Provides instant responses to frequently asked questions about company
    basics, contacts, and common processes.
    """
    try:
        query_lower = query.lower()
        
        # Common quick answers
        quick_answers = {
            "wifi": "Office WiFi: Network 'CompanyGuest', Password: 'Welcome2024!' (visitors)",
            "coffee": "Free coffee on 2nd floor kitchen, premium coffee bar on 3rd floor",
            "parking": "Parking garage entrance on 5th St, badge required after 6 PM",
            "lunch": "Cafeteria open 11:30 AM - 2:30 PM, food trucks Tue/Thu outside",
            "gym": "On-site gym on basement level, 24/7 access with badge",
            "sick": "Use unlimited PTO for sick days, no doctor's note needed under 3 days",
            "manager": "Find your manager in BambooHR or ask #people-ops",
            "payroll": "Questions about pay/benefits: contact payroll@company.com",
            "it": "IT emergencies: #it-support channel or ext. 911",
            "security": "Security issues: badge@company.com or #security channel"
        }
        
        # Check for quick answer matches
        for keyword, answer in quick_answers.items():
            if keyword in query_lower:
                return json.dumps({
                    "success": True,
                    "type": "quick_answer",
                    "query": query,
                    "answer": answer,
                    "note": "For more detailed information, try a specific knowledge search"
                })
        
        # No quick answer found
        return json.dumps({
            "success": False,
            "message": "No quick answer available for this query",
            "suggestion": "Try using the knowledge base search for more detailed information"
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error getting quick answer: {str(e)}"
        })

# --- Tool Aggregator ---

def get_knowledge_tools():
    """Returns a list of all knowledge base tools in this module."""
    return [
        search_knowledge_base,
        get_document_with_context,
        create_service_request,
        get_quick_answers
    ]