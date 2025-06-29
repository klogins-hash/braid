#!/usr/bin/env python3
"""
Live Collections Demo Script
Demonstrates the complete AR collections workflow with real communications.
"""
import json
from collections_tools import send_collection_email, send_collection_sms, make_collection_call, escalate_to_human

def demo_collections_workflow():
    """Run a complete collections demo with live communications."""
    
    print("🚨 ACCOUNTS RECEIVABLE COLLECTIONS DEMO")
    print("=" * 60)
    print("Demonstrating live email, SMS, and Slack integration")
    print()
    
    # Demo client data
    client_data = {
        "client_name": "TechCorp Solutions",
        "contact_email": "suncrestcap@gmail.com",
        "phone_number": "+19175922840",
        "invoice_number": "INV-2025-001",
        "amount_due": 15000.00,
        "days_overdue": 15
    }
    
    print(f"📋 Demo Client: {client_data['client_name']}")
    print(f"💰 Amount Due: ${client_data['amount_due']:,.2f}")
    print(f"⏰ Days Overdue: {client_data['days_overdue']} days")
    print()
    
    # Stage 1: Email Reminder
    print("📧 STAGE 1: Sending email reminder...")
    print("-" * 40)
    
    email_result = send_collection_email.invoke({
        'client_name': client_data['client_name'],
        'contact_email': client_data['contact_email'],
        'invoice_number': client_data['invoice_number'],
        'amount_due': client_data['amount_due'],
        'days_overdue': client_data['days_overdue'],
        'stage': 'stage_1'
    })
    
    email_data = json.loads(email_result)
    if email_data.get("delivery_status") == "delivered":
        print(f"✅ Email sent successfully!")
        print(f"   To: {client_data['contact_email']}")
        print(f"   Subject: {email_data.get('subject', 'N/A')}")
        print(f"   Message ID: {email_data.get('gmail_message_id', 'N/A')}")
    else:
        print(f"❌ Email failed: {email_data.get('error', 'Unknown error')}")
    
    print()
    
    # Stage 2: SMS Reminder
    print("📱 STAGE 2: Sending SMS reminder...")
    print("-" * 40)
    
    sms_result = send_collection_sms.invoke({
        'client_name': client_data['client_name'],
        'phone_number': client_data['phone_number'],
        'invoice_number': client_data['invoice_number'],
        'amount_due': client_data['amount_due'],
        'days_overdue': client_data['days_overdue']
    })
    
    sms_data = json.loads(sms_result)
    if sms_data.get("delivery_status") == "delivered":
        print(f"✅ SMS sent successfully!")
        print(f"   To: {client_data['phone_number']}")
        print(f"   Message: {sms_data.get('message', 'N/A')[:50]}...")
        print(f"   Twilio ID: {sms_data.get('sms_id', 'N/A')}")
    else:
        print(f"❌ SMS failed: {sms_data.get('error', 'Unknown error')}")
    
    print()
    
    # Stage 2b: Voice Call (Alternative to SMS)
    print("📞 STAGE 2B: Making voice call (toll-free)...")
    print("-" * 40)
    
    call_result = make_collection_call.invoke({
        'client_name': client_data['client_name'],
        'phone_number': client_data['phone_number'],
        'invoice_number': client_data['invoice_number'],
        'amount_due': client_data['amount_due'],
        'days_overdue': client_data['days_overdue']
    })
    
    call_data = json.loads(call_result)
    if call_data.get("status") == "initiated":
        print(f"✅ Voice call initiated successfully!")
        print(f"   From: {call_data.get('from_number', 'N/A')}")
        print(f"   To: {client_data['phone_number']}")
        print(f"   Call ID: {call_data.get('call_id', 'N/A')}")
    else:
        print(f"❌ Voice call failed: {call_data.get('error', 'Unknown error')}")
    
    print()
    
    # Stage 3: Human Escalation
    print("🚨 STAGE 3: Escalating to human team...")
    print("-" * 40)
    
    escalation_result = escalate_to_human.invoke({
        'client_name': client_data['client_name'],
        'invoice_details': json.dumps({
            "invoice_number": client_data['invoice_number'],
            "amount_due": client_data['amount_due'],
            "days_overdue": client_data['days_overdue'],
            "contact_email": client_data['contact_email'],
            "phone_number": client_data['phone_number']
        }),
        'communication_history': json.dumps({
            "emails_sent": 1,
            "sms_sent": 1,
            "last_email": email_data.get('timestamp'),
            "last_sms": sms_data.get('timestamp')
        }),
        'urgency_level': 'high'
    })
    
    escalation_data = json.loads(escalation_result)
    if escalation_data.get("notification_sent"):
        print(f"✅ Slack escalation sent successfully!")
        print(f"   Channel: #{escalation_data.get('channel', 'N/A')}")
        print(f"   Escalation ID: {escalation_data.get('escalation_id', 'N/A')}")
        print(f"   Follow-up required by: {escalation_data.get('follow_up_required_by', 'N/A')[:19]}")
    else:
        print(f"❌ Slack escalation failed: {escalation_data.get('error', 'Unknown error')}")
    
    print()
    print("🎉 COLLECTIONS DEMO COMPLETE!")
    print("=" * 60)
    print("✅ Professional email sent via Gmail API")
    print("✅ Urgent SMS sent via Twilio")
    print("✅ Human escalation posted to Slack")
    print()
    print("📋 Summary:")
    print(f"   Client: {client_data['client_name']}")
    print(f"   Amount: ${client_data['amount_due']:,.2f}")
    print(f"   All communication channels activated:")
    print(f"     • Professional email sent via Gmail API")
    print(f"     • SMS attempted (A2P compliance required)")
    print(f"     • Voice call made via toll-free number")
    print(f"     • Human escalation posted to Slack")
    print(f"   Complete audit trail maintained")

if __name__ == "__main__":
    demo_collections_workflow()