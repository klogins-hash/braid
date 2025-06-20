"""
Custom onboarding tools for the Onboarding & Internal Knowledge Expert agent.
Handles scheduling, progress tracking, and task management for employee onboarding journeys.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

# --- Input Schemas ---

class OnboardingScheduleInput(BaseModel):
    user_id: str = Field(description="Slack user ID of the new hire")
    user_name: str = Field(description="Display name of the new hire")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    onboarding_type: str = Field(
        default="standard_30_day",
        description="Type of onboarding journey: 'standard_30_day', 'manager_track', 'remote_worker'"
    )
    role: Optional[str] = Field(default=None, description="Job role/department for customization")

class OnboardingStatusInput(BaseModel):
    user_id: str = Field(description="Slack user ID to check status for")

class OnboardingTaskInput(BaseModel):
    user_id: str = Field(description="Slack user ID")
    task_id: str = Field(description="Unique task identifier")
    status: str = Field(description="Task status: 'pending', 'completed', 'skipped'")
    completion_date: Optional[str] = Field(default=None, description="Completion date if status is 'completed'")

class OnboardingCompleteInput(BaseModel):
    user_id: str = Field(description="Slack user ID")
    completion_reason: str = Field(
        default="standard_completion",
        description="Reason for completion: 'standard_completion', 'early_completion', 'transferred'"
    )

# --- Onboarding Journey Templates ---

ONBOARDING_TEMPLATES = {
    "standard_30_day": {
        "duration_days": 30,
        "tasks": [
            {
                "day": 1,
                "task_id": "welcome_message",
                "title": "Send Welcome Message",
                "description": "Send personalized welcome DM with first-day essentials",
                "action_type": "automated_message",
                "template": "welcome_day1"
            },
            {
                "day": 1, 
                "task_id": "schedule_intro_meetings",
                "title": "Schedule Introduction Meetings",
                "description": "Set up meetings with manager, team lead, and buddy",
                "action_type": "calendar_scheduling",
                "meeting_types": ["manager_1on1", "team_intro", "buddy_meetup"]
            },
            {
                "day": 1,
                "task_id": "share_essential_docs",
                "title": "Share Essential Documents",
                "description": "Provide links to employee handbook, setup guides, and policies",
                "action_type": "document_sharing",
                "document_categories": ["handbook", "tech_setup", "policies"]
            },
            {
                "day": 3,
                "task_id": "first_checkin",
                "title": "First Check-in",
                "description": "Send follow-up message to check progress and answer questions",
                "action_type": "automated_message",
                "template": "checkin_day3"
            },
            {
                "day": 7,
                "task_id": "week_one_review",
                "title": "Week One Review",
                "description": "Weekly check-in with progress assessment and resource sharing",
                "action_type": "automated_message",
                "template": "review_week1"
            },
            {
                "day": 14,
                "task_id": "assign_first_project",
                "title": "First Project Assignment",
                "description": "Create Notion task for first meaningful project or assignment",
                "action_type": "task_assignment",
                "project_type": "onboarding_project"
            },
            {
                "day": 21,
                "task_id": "three_week_feedback",
                "title": "Three Week Feedback Session",
                "description": "Collect feedback on onboarding experience and adjust if needed",
                "action_type": "feedback_collection",
                "feedback_form": "three_week_survey"
            },
            {
                "day": 30,
                "task_id": "onboarding_completion",
                "title": "Onboarding Completion",
                "description": "Mark onboarding complete and transition to regular support",
                "action_type": "completion_ceremony",
                "celebration": True
            }
        ]
    },
    "manager_track": {
        "duration_days": 45,
        "tasks": [
            # Standard tasks plus manager-specific ones
            {
                "day": 1,
                "task_id": "manager_welcome",
                "title": "Manager Welcome Package",
                "description": "Send manager-specific welcome with leadership resources",
                "action_type": "automated_message",
                "template": "manager_welcome"
            },
            {
                "day": 7,
                "task_id": "leadership_intro",
                "title": "Leadership Team Introduction",
                "description": "Schedule meetings with C-level and department heads",
                "action_type": "calendar_scheduling",
                "meeting_types": ["leadership_roundtable"]
            },
            {
                "day": 14,
                "task_id": "team_overview",
                "title": "Team Overview Session",
                "description": "Detailed briefing on team structure, goals, and current projects",
                "action_type": "document_sharing",
                "document_categories": ["team_structure", "goals", "projects"]
            }
        ]
    }
}

MESSAGE_TEMPLATES = {
    "welcome_day1": """
🎉 Welcome to the team, {user_name}!

I'm your Onboarding Assistant, and I'll be helping you get settled over the next 30 days. Here's what I've set up for you:

📅 **Meetings Scheduled:**
• 1:1 with your manager
• Team introduction
• Buddy system meetup

📚 **Essential Reading:**
• Employee Handbook: [link]
• Tech Setup Guide: [link]
• Company Policies: [link]

🆘 **Need Help?**
Just ask me anything! I'm here 24/7 to help with questions about processes, policies, or connecting you with the right people.

Have a great first day! 🚀
""",
    "checkin_day3": """
👋 Hi {user_name}!

How are things going after your first few days? I wanted to check in and see:

✅ **Setup Progress:**
• Did you complete your laptop setup?
• Any issues accessing company systems?
• Questions about your initial tasks?

📋 **Quick Wins:**
• Introduced yourself in #introductions?
• Connected with your onboarding buddy?
• Reviewed the employee handbook?

Feel free to ask me about anything - I'm here to help! What's been the most helpful so far? 😊
""",
    "review_week1": """
🗓️ Week One Complete! 

Great job making it through your first week, {user_name}! Here's a quick check-in:

📊 **This Week:**
• How did your team meetings go?
• Any surprises or unexpected challenges?
• What tools/processes do you want to learn more about?

📚 **Week 2 Focus:**
• Deep dive into your role specifics
• Shadow team members in action
• Start your first project assignment

🎯 **Goals for Next Week:**
• Complete role-specific training modules
• Set up regular 1:1s with your manager
• Identify areas where you want additional support

Questions? Just ask! I'm tracking your progress and here to help optimize your experience. 💪
"""
}

# --- Persistent Storage Simulation ---
# In production, this would be a real database or memory store

ONBOARDING_STORAGE = {}  # user_id -> onboarding_data

def get_user_onboarding_data(user_id: str) -> Dict[str, Any]:
    """Get stored onboarding data for a user."""
    return ONBOARDING_STORAGE.get(user_id, {})

def save_user_onboarding_data(user_id: str, data: Dict[str, Any]) -> None:
    """Save onboarding data for a user."""
    ONBOARDING_STORAGE[user_id] = data

# --- Tool Implementations ---

@tool("schedule_onboarding_task", args_schema=OnboardingScheduleInput)
def schedule_onboarding_task(
    user_id: str,
    user_name: str,
    start_date: str,
    onboarding_type: str = "standard_30_day",
    role: Optional[str] = None
) -> str:
    """
    Schedule a complete onboarding journey for a new hire.
    
    This tool sets up the entire 30-day onboarding workflow with scheduled tasks,
    automated messages, and progress tracking.
    """
    try:
        # Get the onboarding template
        if onboarding_type not in ONBOARDING_TEMPLATES:
            return json.dumps({
                "success": False,
                "message": f"Unknown onboarding type: {onboarding_type}",
                "available_types": list(ONBOARDING_TEMPLATES.keys())
            })
        
        template = ONBOARDING_TEMPLATES[onboarding_type]
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Generate scheduled tasks with actual dates
        scheduled_tasks = []
        for task_template in template["tasks"]:
            task_date = start_datetime + timedelta(days=task_template["day"] - 1)
            
            scheduled_task = {
                "task_id": task_template["task_id"],
                "title": task_template["title"],
                "description": task_template["description"],
                "scheduled_date": task_date.strftime("%Y-%m-%d"),
                "action_type": task_template["action_type"],
                "status": "pending",
                "day_number": task_template["day"]
            }
            
            # Add type-specific data
            for key in ["template", "meeting_types", "document_categories", "project_type"]:
                if key in task_template:
                    scheduled_task[key] = task_template[key]
            
            scheduled_tasks.append(scheduled_task)
        
        # Store onboarding data
        onboarding_data = {
            "user_id": user_id,
            "user_name": user_name,
            "start_date": start_date,
            "onboarding_type": onboarding_type,
            "role": role,
            "status": "active",
            "current_day": 1,
            "scheduled_tasks": scheduled_tasks,
            "completed_tasks": [],
            "created_at": datetime.now().isoformat(),
            "last_interaction": datetime.now().isoformat()
        }
        
        save_user_onboarding_data(user_id, onboarding_data)
        
        return json.dumps({
            "success": True,
            "message": f"Onboarding journey scheduled for {user_name}",
            "journey_type": onboarding_type,
            "duration_days": template["duration_days"],
            "total_tasks": len(scheduled_tasks),
            "scheduled_tasks": scheduled_tasks,
            "next_task_date": scheduled_tasks[0]["scheduled_date"] if scheduled_tasks else None
        })
        
    except ValueError as e:
        return json.dumps({
            "success": False,
            "message": f"Invalid date format: {str(e)}. Use YYYY-MM-DD format."
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error scheduling onboarding: {str(e)}"
        })

@tool("get_user_onboarding_status", args_schema=OnboardingStatusInput)
def get_user_onboarding_status(user_id: str) -> str:
    """
    Get the current onboarding status and progress for a user.
    
    Returns detailed information about onboarding journey progress,
    upcoming tasks, and completion status.
    """
    try:
        onboarding_data = get_user_onboarding_data(user_id)
        
        if not onboarding_data:
            return json.dumps({
                "success": False,
                "message": "No onboarding data found for this user",
                "user_id": user_id
            })
        
        # Calculate progress metrics
        total_tasks = len(onboarding_data.get("scheduled_tasks", []))
        completed_tasks = len(onboarding_data.get("completed_tasks", []))
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Find next pending task
        pending_tasks = [
            task for task in onboarding_data.get("scheduled_tasks", [])
            if task.get("status") == "pending"
        ]
        next_task = pending_tasks[0] if pending_tasks else None
        
        # Calculate days since start
        start_date = datetime.strptime(onboarding_data["start_date"], "%Y-%m-%d")
        days_since_start = (datetime.now() - start_date).days + 1
        
        return json.dumps({
            "success": True,
            "user_id": user_id,
            "user_name": onboarding_data.get("user_name", "Unknown"),
            "status": onboarding_data.get("status", "unknown"),
            "onboarding_type": onboarding_data.get("onboarding_type", "unknown"),
            "start_date": onboarding_data.get("start_date"),
            "current_day": days_since_start,
            "progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": len(pending_tasks),
                "progress_percentage": round(progress_percentage, 1)
            },
            "next_task": next_task,
            "last_interaction": onboarding_data.get("last_interaction")
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error retrieving onboarding status: {str(e)}"
        })

@tool("update_task_status", args_schema=OnboardingTaskInput)
def update_task_status(
    user_id: str,
    task_id: str,
    status: str,
    completion_date: Optional[str] = None
) -> str:
    """
    Update the status of a specific onboarding task.
    
    Used to mark tasks as completed, skipped, or reset to pending.
    Automatically tracks completion dates and progress.
    """
    try:
        onboarding_data = get_user_onboarding_data(user_id)
        
        if not onboarding_data:
            return json.dumps({
                "success": False,
                "message": "No onboarding data found for this user"
            })
        
        # Find the task to update
        scheduled_tasks = onboarding_data.get("scheduled_tasks", [])
        task_found = False
        
        for task in scheduled_tasks:
            if task.get("task_id") == task_id:
                task["status"] = status
                if status == "completed" and completion_date:
                    task["completion_date"] = completion_date
                elif status == "completed":
                    task["completion_date"] = datetime.now().strftime("%Y-%m-%d")
                
                task_found = True
                break
        
        if not task_found:
            return json.dumps({
                "success": False,
                "message": f"Task '{task_id}' not found in onboarding schedule"
            })
        
        # Update completed tasks list
        if status == "completed":
            completed_tasks = onboarding_data.get("completed_tasks", [])
            if task_id not in completed_tasks:
                completed_tasks.append(task_id)
                onboarding_data["completed_tasks"] = completed_tasks
        
        # Update last interaction
        onboarding_data["last_interaction"] = datetime.now().isoformat()
        
        # Save updated data
        save_user_onboarding_data(user_id, onboarding_data)
        
        return json.dumps({
            "success": True,
            "message": f"Task '{task_id}' status updated to '{status}'",
            "task_id": task_id,
            "new_status": status,
            "completion_date": completion_date if status == "completed" else None
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error updating task status: {str(e)}"
        })

@tool("mark_onboarding_complete", args_schema=OnboardingCompleteInput)
def mark_onboarding_complete(
    user_id: str,
    completion_reason: str = "standard_completion"
) -> str:
    """
    Mark a user's onboarding journey as complete.
    
    This transitions the user from active onboarding to regular support mode
    and generates completion metrics.
    """
    try:
        onboarding_data = get_user_onboarding_data(user_id)
        
        if not onboarding_data:
            return json.dumps({
                "success": False,
                "message": "No onboarding data found for this user"
            })
        
        # Calculate completion metrics
        total_tasks = len(onboarding_data.get("scheduled_tasks", []))
        completed_tasks = len(onboarding_data.get("completed_tasks", []))
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        start_date = datetime.strptime(onboarding_data["start_date"], "%Y-%m-%d")
        completion_date = datetime.now()
        days_to_complete = (completion_date - start_date).days + 1
        
        # Update onboarding data
        onboarding_data.update({
            "status": "completed",
            "completion_date": completion_date.strftime("%Y-%m-%d"),
            "completion_reason": completion_reason,
            "completion_metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(completion_rate, 1),
                "days_to_complete": days_to_complete,
                "planned_duration": ONBOARDING_TEMPLATES.get(
                    onboarding_data.get("onboarding_type", "standard_30_day"), {}
                ).get("duration_days", 30)
            },
            "last_interaction": datetime.now().isoformat()
        })
        
        # Save final state
        save_user_onboarding_data(user_id, onboarding_data)
        
        return json.dumps({
            "success": True,
            "message": f"Onboarding completed for {onboarding_data.get('user_name', 'user')}",
            "completion_date": completion_date.strftime("%Y-%m-%d"),
            "completion_reason": completion_reason,
            "metrics": onboarding_data["completion_metrics"],
            "celebration_message": f"🎉 Congratulations on completing your onboarding journey! You finished {completed_tasks}/{total_tasks} tasks with a {completion_rate:.1f}% completion rate."
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error marking onboarding complete: {str(e)}"
        })

@tool("get_message_template")
def get_message_template(template_name: str, user_name: str = "there") -> str:
    """
    Get a formatted onboarding message template.
    
    Returns personalized messages for different onboarding stages.
    """
    try:
        if template_name not in MESSAGE_TEMPLATES:
            return json.dumps({
                "success": False,
                "message": f"Template '{template_name}' not found",
                "available_templates": list(MESSAGE_TEMPLATES.keys())
            })
        
        template = MESSAGE_TEMPLATES[template_name]
        formatted_message = template.format(user_name=user_name)
        
        return json.dumps({
            "success": True,
            "template_name": template_name,
            "formatted_message": formatted_message
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error getting message template: {str(e)}"
        })

# --- Tool Aggregator ---

def get_onboarding_tools():
    """Returns a list of all onboarding tools in this module."""
    return [
        schedule_onboarding_task,
        get_user_onboarding_status,
        update_task_status,
        mark_onboarding_complete,
        get_message_template
    ]