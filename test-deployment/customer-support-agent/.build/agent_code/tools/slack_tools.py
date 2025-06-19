"""
Slack integration tools for customer support agent.
"""

import os
from typing import Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    """Slack integration for customer support notifications."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize Slack client.
        
        Args:
            token: Slack bot token. If None, reads from SLACK_BOT_TOKEN env var.
        """
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        if self.token:
            self.client = WebClient(token=self.token)
        else:
            self.client = None
            print("⚠️ Slack token not provided - notifications will be simulated")
    
    def send_escalation_alert(
        self,
        channel: str,
        ticket_id: str,
        customer_id: str,
        issue: str,
        priority: str
    ) -> Dict[str, Any]:
        """Send escalation alert to Slack channel.
        
        Args:
            channel: Slack channel name or ID
            ticket_id: Support ticket ID
            customer_id: Customer identifier
            issue: Issue description
            priority: Issue priority level
            
        Returns:
            Result of the Slack API call
        """
        priority_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "ℹ️",
            "low": "📝"
        }
        
        emoji = priority_emoji.get(priority, "📝")
        
        message = f"""
{emoji} *CUSTOMER SUPPORT ESCALATION*

*Ticket:* {ticket_id}
*Customer:* {customer_id}
*Priority:* {priority.upper()}

*Issue:*
> {issue}

*Actions Required:*
• Review customer history
• Contact customer within SLA timeframe
• Update ticket status when resolved

*Quick Actions:*
• <https://notion.so/tickets/{ticket_id}|View Ticket>
• <https://crm.company.com/customer/{customer_id}|Customer Profile>
"""
        
        if self.client:
            try:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=f"Support Escalation: {ticket_id}",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": message
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Take Ownership"
                                    },
                                    "value": f"take_ownership_{ticket_id}",
                                    "action_id": "take_ownership"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View Ticket"
                                    },
                                    "url": f"https://notion.so/tickets/{ticket_id}"
                                }
                            ]
                        }
                    ]
                )
                
                return {
                    "success": True,
                    "message_ts": response["ts"],
                    "channel": response["channel"]
                }
                
            except SlackApiError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            # Simulate success for demo
            print(f"📱 [SLACK SIMULATION] Escalation alert sent to #{channel}")
            print(f"   Ticket: {ticket_id} | Priority: {priority}")
            print(f"   Message: {issue[:50]}...")
            
            return {
                "success": True,
                "message_ts": "simulated_timestamp",
                "channel": channel,
                "simulated": True
            }
    
    def send_team_notification(
        self,
        channel: str,
        message: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send general team notification.
        
        Args:
            channel: Slack channel name or ID
            message: Message to send
            thread_ts: Optional thread timestamp for replies
            
        Returns:
            Result of the Slack API call
        """
        if self.client:
            try:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=message,
                    thread_ts=thread_ts
                )
                
                return {
                    "success": True,
                    "message_ts": response["ts"],
                    "channel": response["channel"]
                }
                
            except SlackApiError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            # Simulate success for demo
            print(f"📱 [SLACK SIMULATION] Team notification sent to #{channel}")
            print(f"   Message: {message[:50]}...")
            
            return {
                "success": True,
                "message_ts": "simulated_timestamp",
                "channel": channel,
                "simulated": True
            }
    
    def update_escalation_status(
        self,
        channel: str,
        message_ts: str,
        status: str,
        assigned_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update escalation message with current status.
        
        Args:
            channel: Slack channel name or ID
            message_ts: Original message timestamp
            status: Current status (assigned, in_progress, resolved)
            assigned_to: Agent assigned to the ticket
            
        Returns:
            Result of the update operation
        """
        status_emoji = {
            "assigned": "👥",
            "in_progress": "⚙️",
            "resolved": "✅"
        }
        
        emoji = status_emoji.get(status, "📝")
        
        status_text = f"{emoji} *Status Update: {status.replace('_', ' ').title()}*"
        if assigned_to:
            status_text += f"\n*Assigned to:* {assigned_to}"
        
        if self.client:
            try:
                # Note: In a real implementation, you'd update the original message
                # For demo, we'll send a thread reply
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=status_text,
                    thread_ts=message_ts
                )
                
                return {
                    "success": True,
                    "message_ts": response["ts"],
                    "channel": response["channel"]
                }
                
            except SlackApiError as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            # Simulate success for demo
            print(f"📱 [SLACK SIMULATION] Status update sent to #{channel}")
            print(f"   Status: {status} | Assigned to: {assigned_to}")
            
            return {
                "success": True,
                "message_ts": "simulated_timestamp",
                "channel": channel,
                "simulated": True
            }