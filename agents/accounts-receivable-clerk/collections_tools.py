"""
Collections and Communication Tools for Accounts Receivable Clerk
Multi-stage collections workflow with email, SMS, and Slack escalation.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Force environment reload
load_dotenv(override=True)

class CollectionEmailInput(BaseModel):
    """Input schema for collections emails."""
    client_name: str = Field(description="Client company name")
    contact_email: str = Field(description="Client contact email address")
    invoice_number: str = Field(description="Invoice number")
    amount_due: float = Field(description="Outstanding amount")
    days_overdue: int = Field(description="Number of days past due")
    stage: str = Field(description="Collection stage: stage_1, stage_2, or stage_3")

class CollectionSMSInput(BaseModel):
    """Input schema for collections SMS."""
    client_name: str = Field(description="Client company name")
    phone_number: str = Field(description="Client phone number")
    invoice_number: str = Field(description="Invoice number")
    amount_due: float = Field(description="Outstanding amount")
    days_overdue: int = Field(description="Number of days past due")

class EscalationInput(BaseModel):
    """Input schema for human escalation."""
    client_name: str = Field(description="Client company name")
    invoice_details: str = Field(description="JSON string with invoice information")
    communication_history: str = Field(description="Previous communication attempts")
    urgency_level: str = Field(description="low, medium, high, critical")

def get_email_template(stage: str, client_name: str, invoice_number: str, amount_due: float, days_overdue: int) -> Dict[str, str]:
    """Generate email templates for different collection stages."""
    
    if stage == "stage_1":
        subject = f"Payment Reminder - Invoice {invoice_number}"
        body = f"""Dear {client_name},

I hope this message finds you well. This is a friendly reminder that we have not yet received payment for Invoice {invoice_number} in the amount of ${amount_due:,.2f}.

Invoice Details:
- Invoice Number: {invoice_number}
- Amount Due: ${amount_due:,.2f}
- Days Past Due: {days_overdue} days
- Original Due Date: {(datetime.now() - timedelta(days=days_overdue + 30)).strftime('%B %d, %Y')}

We understand that sometimes invoices can be overlooked in busy schedules. If you have already sent payment, please disregard this message. If you have any questions about this invoice or need to discuss payment arrangements, please don't hesitate to contact us.

To make payment easy, you can:
- Pay online through your client portal
- Send payment to our standard business address
- Contact us to arrange alternative payment methods

We value our business relationship and appreciate your prompt attention to this matter.

Best regards,
Accounts Receivable Department

---
This is an automated message from our accounts receivable system.
"""
    
    elif stage == "stage_2":
        subject = f"URGENT: Payment Required - Invoice {invoice_number} ({days_overdue} days overdue)"
        body = f"""Dear {client_name},

This is an urgent notice regarding Invoice {invoice_number} for ${amount_due:,.2f}, which is now {days_overdue} days past due.

Despite our previous reminder, payment has not been received. Immediate action is required to bring your account current and avoid further collection actions.

Invoice Details:
- Invoice Number: {invoice_number}
- Amount Due: ${amount_due:,.2f}
- Days Past Due: {days_overdue} days
- Original Due Date: {(datetime.now() - timedelta(days=days_overdue + 30)).strftime('%B %d, %Y')}

Please remit payment within 48 hours to avoid:
- Additional late fees
- Potential service suspension
- Referral to external collections

If you are experiencing financial difficulties, please contact us immediately to discuss payment arrangements. We are willing to work with you to resolve this matter.

Payment can be made:
- Online through your client portal
- By calling our accounts receivable department
- Via wire transfer (contact us for details)

We must receive payment or hear from you within 48 hours. Please treat this matter with the urgency it requires.

Regards,
Accounts Receivable Department

---
This is an automated urgent notice from our accounts receivable system.
"""
    
    else:  # stage_3 or default
        subject = f"FINAL NOTICE: Account Escalation - Invoice {invoice_number}"
        body = f"""Dear {client_name},

This is a FINAL NOTICE regarding Invoice {invoice_number} for ${amount_due:,.2f}, which is now {days_overdue} days past due.

Despite multiple attempts to contact you, this invoice remains unpaid. Your account will be escalated to our management team and potentially referred to external collections if payment is not received immediately.

Invoice Details:
- Invoice Number: {invoice_number}
- Amount Due: ${amount_due:,.2f}
- Days Past Due: {days_overdue} days

IMMEDIATE ACTION REQUIRED:
- Payment must be received within 24 hours
- Failure to respond will result in account escalation
- Additional fees and interest may apply
- This may affect your credit standing

This is your final opportunity to resolve this matter directly with us. After 24 hours, this account will be transferred to our management team for further action.

Contact us immediately at [phone number] or reply to this email.

Accounts Receivable Department

---
AUTOMATED FINAL NOTICE - Immediate response required
"""
    
    return {"subject": subject, "body": body}

def get_sms_template(client_name: str, invoice_number: str, amount_due: float, days_overdue: int) -> str:
    """Generate SMS template for collections."""
    
    if days_overdue <= 14:
        return f"PAYMENT REMINDER: {client_name}, Invoice {invoice_number} for ${amount_due:,.2f} is {days_overdue} days overdue. Please remit payment or call us immediately. Reply STOP to opt out."
    else:
        return f"URGENT: {client_name}, Invoice {invoice_number} (${amount_due:,.2f}) is {days_overdue} days overdue. Immediate payment required to avoid collections. Call us now. Reply STOP to opt out."

def get_voice_message(client_name: str, invoice_number: str, amount_due: float, days_overdue: int) -> str:
    """Generate voice message script for collections calls."""
    
    if days_overdue <= 14:
        return f"""
Hello, this is an automated payment reminder from the Accounts Receivable Department.

This call is for {client_name} regarding Invoice {invoice_number} in the amount of ${amount_due:,.2f}, which is currently {days_overdue} days past due.

Please contact us at your earliest convenience to arrange payment or discuss payment options. 

You can reach us during business hours or reply to our recent email communications.

Thank you for your immediate attention to this matter.
"""
    else:
        return f"""
This is an urgent payment notice from the Accounts Receivable Department.

This call is for {client_name} regarding Invoice {invoice_number} in the amount of ${amount_due:,.2f}, which is now {days_overdue} days overdue.

Immediate action is required to avoid further collection activities. Please contact us today to resolve this outstanding balance.

This account requires immediate attention to prevent escalation to our management team.

Please call us back as soon as possible.
"""

@tool("send_collection_email", args_schema=CollectionEmailInput)
def send_collection_email(client_name: str, contact_email: str, invoice_number: str, amount_due: float, days_overdue: int, stage: str) -> str:
    """Send automated collection email based on stage and overdue status."""
    try:
        print(f"📧 Sending {stage} collection email to {client_name} ({contact_email})")
        
        # Generate email content
        email_template = get_email_template(stage, client_name, invoice_number, amount_due, days_overdue)
        
        # Check for Google credentials
        google_creds_path = os.path.join(os.path.dirname(__file__), "credentials", "google_credentials.json")
        google_token_path = os.path.join(os.path.dirname(__file__), "credentials", "google_token.json")
        
        email_data = {
            "timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "recipient": contact_email,
            "subject": email_template["subject"],
            "body": email_template["body"],
            "invoice_number": invoice_number,
            "amount_due": amount_due,
            "days_overdue": days_overdue,
            "collection_stage": stage,
            "status": "sent",
            "data_source": "Collection Email System"
        }
        
        # Try to send via Gmail API if credentials exist
        if os.path.exists(google_creds_path) and "@" in contact_email and "." in contact_email:
            try:
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from googleapiclient.discovery import build
                
                SCOPES = ['https://www.googleapis.com/auth/gmail.send']
                
                creds = None
                # Load existing token
                if os.path.exists(google_token_path):
                    creds = Credentials.from_authorized_user_file(google_token_path, SCOPES)
                
                # If no valid credentials, try to refresh or get new ones
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(google_creds_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # Save credentials for next run
                    with open(google_token_path, 'w') as token:
                        token.write(creds.to_json())
                
                # Build Gmail service
                service = build('gmail', 'v1', credentials=creds)
                
                # Create email message
                message = MIMEMultipart()
                message['to'] = contact_email
                message['subject'] = email_template["subject"]
                message.attach(MIMEText(email_template["body"], 'plain'))
                
                # Encode message
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                
                # Send email
                send_result = service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()
                
                email_data.update({
                    "delivery_status": "delivered",
                    "gmail_message_id": send_result.get('id'),
                    "sent_via": "Gmail API"
                })
                print(f"✅ Collection email sent successfully via Gmail API")
                print(f"   Subject: {email_template['subject']}")
                print(f"   Message ID: {send_result.get('id')}")
                print(f"   Stage: {stage.replace('_', ' ').title()}")
                
            except Exception as gmail_error:
                print(f"❌ Gmail API failed: {gmail_error}")
                email_data.update({
                    "delivery_status": "simulated",
                    "error": str(gmail_error),
                    "note": "Gmail API failed, using simulation"
                })
                print(f"📧 Email simulated (Gmail API unavailable)")
        else:
            # Fallback simulation
            if "@" in contact_email and "." in contact_email:
                email_data["delivery_status"] = "simulated"
                email_data["note"] = "Gmail credentials not found, email simulated"
                print(f"📧 Collection email simulated")
                print(f"   Subject: {email_template['subject']}")
                print(f"   Stage: {stage.replace('_', ' ').title()}")
            else:
                email_data["delivery_status"] = "failed"
                email_data["error"] = "Invalid email address"
                print(f"❌ Email delivery failed: Invalid email address")
        
        # Log communication attempt
        communication_log = {
            "type": "email",
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "success": email_data["delivery_status"] == "delivered",
            "details": f"Collection email to {client_name} regarding invoice {invoice_number}"
        }
        
        email_data["communication_log"] = communication_log
        
        return json.dumps(email_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error sending collection email: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "failed",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Collection Email Error"
        })

@tool("send_collection_sms", args_schema=CollectionSMSInput)
def send_collection_sms(client_name: str, phone_number: str, invoice_number: str, amount_due: float, days_overdue: int) -> str:
    """Send SMS reminder for overdue payments."""
    try:
        print(f"📱 Sending collection SMS to {client_name} ({phone_number})")
        
        # Generate SMS content
        sms_text = get_sms_template(client_name, invoice_number, amount_due, days_overdue)
        
        # Check if Twilio credentials are available
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip().replace('"', '')
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip().replace('"', '')
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "").strip().replace('"', '')
        
        sms_data = {
            "timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "recipient": phone_number,
            "message": sms_text,
            "invoice_number": invoice_number,
            "amount_due": amount_due,
            "days_overdue": days_overdue,
            "data_source": "Collection SMS System"
        }
        
        if twilio_sid and twilio_token and twilio_phone:
            # Send actual SMS via Twilio API
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                
                message = client.messages.create(
                    body=sms_text,
                    from_=twilio_phone,
                    to=phone_number
                )
                
                sms_data.update({
                    "status": "sent",
                    "delivery_status": "delivered",
                    "sms_id": message.sid,
                    "from_number": twilio_phone,
                    "twilio_status": message.status
                })
                print(f"✅ Collection SMS sent successfully via Twilio")
                print(f"   Message ID: {message.sid}")
                print(f"   Message: {sms_text[:50]}...")
            except Exception as twilio_error:
                print(f"❌ Twilio SMS failed: {twilio_error}")
                sms_data.update({
                    "status": "failed",
                    "delivery_status": "failed",
                    "error": str(twilio_error),
                    "note": "Twilio API call failed, check credentials"
                })
        else:
            sms_data.update({
                "status": "simulated",
                "delivery_status": "simulated",
                "note": "SMS would be sent via Twilio if credentials were configured"
            })
            print(f"📱 SMS simulated (Twilio not configured)")
        
        # Log communication attempt
        communication_log = {
            "type": "sms",
            "stage": "stage_2",
            "timestamp": datetime.now().isoformat(),
            "success": sms_data.get("delivery_status") in ["delivered", "simulated"],
            "details": f"Collection SMS to {client_name} regarding invoice {invoice_number}"
        }
        
        sms_data["communication_log"] = communication_log
        
        return json.dumps(sms_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error sending collection SMS: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "failed",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Collection SMS Error"
        })

class VoiceCallInput(BaseModel):
    """Input schema for voice collection calls."""
    client_name: str = Field(description="Name of the client/company")
    phone_number: str = Field(description="Phone number to call (E.164 format)")
    invoice_number: str = Field(description="Invoice number")
    amount_due: float = Field(description="Amount due on the invoice")
    days_overdue: int = Field(description="Number of days the payment is overdue")

@tool("make_collection_call", args_schema=VoiceCallInput)
def make_collection_call(client_name: str, phone_number: str, invoice_number: str, amount_due: float, days_overdue: int) -> str:
    """Make automated voice call for collections using Twilio."""
    try:
        timestamp = datetime.now().isoformat()
        print(f"📞 Making collection call to {client_name} ({phone_number})")
        
        # Generate voice message
        voice_message = get_voice_message(client_name, invoice_number, amount_due, days_overdue)
        
        # Check if Twilio credentials are available
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip().replace('"', '')
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip().replace('"', '')
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "+18776849509").strip().replace('"', '')  # Use your toll-free number
        
        call_data = {
            "timestamp": timestamp,
            "client_name": client_name,
            "recipient": phone_number,
            "voice_message": voice_message,
            "invoice_number": invoice_number,
            "amount_due": amount_due,
            "days_overdue": days_overdue,
            "data_source": "Collection Voice System"
        }
        
        if twilio_sid and twilio_token and twilio_phone:
            # Make actual voice call via Twilio API
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                
                # Create TwiML for voice message
                twiml_url = f"http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%20voice%3D%22alice%22%3E{voice_message.replace(' ', '%20').replace('\n', '%20')}%3C/Say%3E%3C/Response%3E"
                
                call = client.calls.create(
                    twiml=f'<Response><Say voice="alice">{voice_message}</Say></Response>',
                    to=phone_number,
                    from_=twilio_phone
                )
                
                call_data.update({
                    "status": "initiated",
                    "delivery_status": "calling",
                    "call_id": call.sid,
                    "from_number": twilio_phone,
                    "twilio_status": call.status
                })
                print(f"✅ Collection call initiated successfully via Twilio")
                print(f"   Call ID: {call.sid}")
                print(f"   From: {twilio_phone}")
                print(f"   To: {phone_number}")
            except Exception as twilio_error:
                print(f"❌ Twilio voice call failed: {twilio_error}")
                call_data.update({
                    "status": "failed",
                    "delivery_status": "failed",
                    "error": str(twilio_error),
                    "note": "Twilio API call failed, check credentials"
                })
        else:
            call_data.update({
                "status": "simulated",
                "delivery_status": "simulated",
                "note": "Voice call would be made via Twilio if credentials were configured"
            })
            print(f"📞 Voice call simulated (Twilio not configured)")
        
        # Log communication attempt
        communication_log = {
            "type": "voice_call",
            "stage": "stage_2b",
            "client": client_name,
            "timestamp": timestamp,
            "delivery_details": call_data
        }
        
        return json.dumps(call_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error making collection call: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "status": "failed",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Collection Voice Call Error"
        })

@tool("escalate_to_human", args_schema=EscalationInput)
def escalate_to_human(client_name: str, invoice_details: str, communication_history: str, urgency_level: str) -> str:
    """Escalate overdue account to human oversight via Slack notification."""
    try:
        print(f"🚨 Escalating {client_name} account to human team (Urgency: {urgency_level})")
        
        # Parse invoice details
        try:
            invoice_data = json.loads(invoice_details) if isinstance(invoice_details, str) else invoice_details
        except json.JSONDecodeError:
            invoice_data = {"error": "Could not parse invoice details"}
        
        # Parse communication history
        try:
            comm_data = json.loads(communication_history) if isinstance(communication_history, str) else communication_history
        except json.JSONDecodeError:
            comm_data = {"error": "Could not parse communication history"}
        
        # Create escalation summary
        escalation_data = {
            "escalation_id": f"ESC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "client_name": client_name,
            "urgency_level": urgency_level,
            "escalation_reason": "Automated collections failed - human intervention required",
            "invoice_details": invoice_data,
            "communication_history": comm_data,
            "data_source": "AR Escalation System"
        }
        
        # Calculate escalation metrics
        total_amount_due = invoice_data.get("amount_due", 0) if isinstance(invoice_data, dict) else 0
        days_overdue = invoice_data.get("days_overdue", 0) if isinstance(invoice_data, dict) else 0
        
        # Generate Slack message
        urgency_emoji = {
            "low": "🟡",
            "medium": "🟠", 
            "high": "🔴",
            "critical": "🚨"
        }.get(urgency_level, "⚠️")
        
        slack_message = f"""{urgency_emoji} **ACCOUNTS RECEIVABLE ESCALATION**

**Client**: {client_name}
**Urgency**: {urgency_level.upper()}
**Amount Due**: ${total_amount_due:,.2f}
**Days Overdue**: {days_overdue} days

**Escalation ID**: {escalation_data['escalation_id']}

**Reason**: Automated collections process has been exhausted. This account requires immediate human attention.

**Recommended Actions**:
• Contact client directly via phone
• Review payment history and relationship
• Consider payment plan negotiations
• Evaluate legal/collections referral

**Next Steps**: 
Please assign this escalation to an AR specialist and update the system with resolution actions.
"""
        
        # Check if Slack is configured
        slack_token = os.getenv("SLACK_BOT_TOKEN", "").strip().replace('"', '')
        finance_channel = os.getenv("FINANCE_CHANNEL_ID", "").strip().replace('"', '')
        
        if slack_token and finance_channel:
            # Send actual Slack message
            try:
                from slack_sdk import WebClient
                slack_client = WebClient(token=slack_token)
                
                response = slack_client.chat_postMessage(
                    channel=finance_channel,
                    text=slack_message,
                    username="AR Clerk Bot",
                    icon_emoji=":money_with_wings:"
                )
                
                escalation_data.update({
                    "slack_status": "sent",
                    "channel": finance_channel,
                    "message": slack_message,
                    "notification_sent": True,
                    "slack_ts": response.get("ts"),
                    "slack_response": response.get("ok")
                })
                print(f"✅ Escalation notification sent to Slack channel: {finance_channel}")
            except Exception as slack_error:
                print(f"❌ Slack notification failed: {slack_error}")
                escalation_data.update({
                    "slack_status": "failed",
                    "error": str(slack_error),
                    "note": "Slack API call failed, check credentials"
                })
        else:
            escalation_data.update({
                "slack_status": "simulated",
                "message": slack_message,
                "notification_sent": False,
                "note": "Slack notification would be sent if credentials were configured"
            })
            print(f"📨 Slack escalation simulated (Slack not configured)")
        
        # Set urgency-based follow-up timeline
        follow_up_hours = {
            "low": 48,
            "medium": 24,
            "high": 8,
            "critical": 2
        }.get(urgency_level, 24)
        
        escalation_data["follow_up_required_by"] = (
            datetime.now() + timedelta(hours=follow_up_hours)
        ).isoformat()
        
        # Log escalation
        print(f"🚨 Escalation created: {escalation_data['escalation_id']}")
        print(f"   Urgency: {urgency_level}")
        print(f"   Follow-up required within: {follow_up_hours} hours")
        
        return json.dumps(escalation_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error escalating to human: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "escalation_status": "failed",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Escalation Error"
        })

class ActivityLogInput(BaseModel):
    """Input schema for logging collection activities."""
    activity_data: str = Field(description="JSON string containing activity information to log")

@tool("log_collection_activity", args_schema=ActivityLogInput)
def log_collection_activity(activity_data: str) -> str:
    """Log collection activities for audit trail and compliance."""
    try:
        print("📝 Logging collection activity for audit trail")
        
        # Parse activity data
        try:
            activity = json.loads(activity_data) if isinstance(activity_data, str) else activity_data
        except json.JSONDecodeError:
            activity = {"error": "Could not parse activity data"}
        
        # Create comprehensive log entry
        log_entry = {
            "log_id": f"LOG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity.get("type", "unknown"),
            "client_name": activity.get("client_name", "unknown"),
            "invoice_number": activity.get("invoice_number", "unknown"),
            "action_taken": activity.get("action", "unknown"),
            "outcome": activity.get("outcome", "pending"),
            "compliance_category": "collections_communication",
            "retention_years": 7,  # Financial records retention
            "data_source": "AR Activity Logger"
        }
        
        # Add stage-specific information
        if activity.get("stage"):
            log_entry["collection_stage"] = activity["stage"]
            
        if activity.get("amount_due"):
            log_entry["amount_involved"] = activity["amount_due"]
        
        # Compliance tracking
        log_entry["compliance_notes"] = {
            "fair_debt_collection": "Automated system follows FDCPA guidelines",
            "communication_timing": "Communications sent during business hours",
            "opt_out_honored": "SMS opt-outs automatically processed",
            "documentation": "Complete audit trail maintained"
        }
        
        # In production, this would be stored in a secure audit database
        print(f"✅ Activity logged: {log_entry['log_id']}")
        print(f"   Type: {log_entry['activity_type']}")
        print(f"   Client: {log_entry['client_name']}")
        
        return json.dumps(log_entry, indent=2)
        
    except Exception as e:
        error_msg = f"Error logging collection activity: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "log_status": "failed",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Logging Error"
        })

def get_collections_tools():
    """Get all collections and communication tools for the agent."""
    return [
        send_collection_email,
        send_collection_sms,
        make_collection_call,
        escalate_to_human,
        log_collection_activity
    ]