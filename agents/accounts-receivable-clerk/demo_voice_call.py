#!/usr/bin/env python3
"""
Voice Call Demo Script
Test the new voice calling functionality for collections.
"""
import json
from collections_tools import make_collection_call

def demo_voice_call():
    """Test voice calling with your toll-free number."""
    
    print("📞 VOICE CALL DEMO")
    print("=" * 50)
    print("Testing voice call functionality with toll-free number")
    print("From: +1 877 684 9509")
    print("To: +1 917 592 2840")
    print()
    
    # Demo client data
    client_data = {
        "client_name": "TechCorp Solutions",
        "phone_number": "+19175922840",
        "invoice_number": "INV-2025-001",
        "amount_due": 15000.00,
        "days_overdue": 15
    }
    
    print(f"📋 Demo Client: {client_data['client_name']}")
    print(f"💰 Amount Due: ${client_data['amount_due']:,.2f}")
    print(f"⏰ Days Overdue: {client_data['days_overdue']} days")
    print()
    
    print("📞 Making collection call...")
    print("-" * 30)
    
    # Make the voice call
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
        print(f"   Status: {call_data.get('twilio_status', 'N/A')}")
    else:
        print(f"❌ Voice call failed: {call_data.get('error', 'Unknown error')}")
        print(f"   Status: {call_data.get('status', 'N/A')}")
    
    print()
    print("📋 Voice Message Preview:")
    print("-" * 30)
    message = call_data.get('voice_message', 'No message available')
    print(message[:200] + "..." if len(message) > 200 else message)
    
    print()
    print("🎉 VOICE CALL DEMO COMPLETE!")
    print("=" * 50)
    print("Check your phone for the incoming call!")

if __name__ == "__main__":
    demo_voice_call()