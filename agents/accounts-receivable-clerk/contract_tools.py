"""
Contract Processing Tools for Accounts Receivable Clerk
Advanced document parsing and contract data extraction capabilities.
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Force environment reload
load_dotenv(override=True)

class ContractInput(BaseModel):
    """Input schema for contract processing."""
    contract_text: str = Field(description="Full contract text or description")
    client_context: Optional[str] = Field(default=None, description="Additional context about the client")

class BillingTermsInput(BaseModel):
    """Input schema for billing terms analysis."""
    terms_text: str = Field(description="Billing terms section from contract")
    total_amount: float = Field(description="Total contract value")

@tool("extract_contract_data", args_schema=ContractInput)
def extract_contract_data(contract_text: str, client_context: str = None) -> str:
    """Extract structured billing data from contract text using AI parsing."""
    try:
        print(f"🔍 Extracting contract data from {len(contract_text)} characters of text")
        
        # Enhanced pattern matching for contract data
        extracted_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "contract_length": len(contract_text),
            "data_source": "AI Contract Parsing"
        }
        
        # Extract client name patterns
        client_patterns = [
            r"(?:Client|Company|Customer):\s*([A-Za-z\s&.,Inc]+)",
            r"([A-Za-z\s&.,Inc]+)\s+(?:hereby agrees|enters into)",
            r"This agreement is between .+ and ([A-Za-z\s&.,Inc]+)",
            r"(?:between|with)\s+([A-Z][A-Za-z\s&.,Inc]{2,30})(?:\s+and|\s+for)"
        ]
        
        client_name = None
        for pattern in client_patterns:
            match = re.search(pattern, contract_text, re.IGNORECASE)
            if match:
                client_name = match.group(1).strip()
                break
        
        if not client_name and client_context:
            client_name = client_context.strip()
        
        extracted_data["client_name"] = client_name or "Not specified"
        
        # Extract email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, contract_text)
        extracted_data["contact_email"] = emails[0] if emails else "Not specified"
        
        # Extract monetary amounts
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?) dollars',
            r'total.*?([0-9,]+(?:\.[0-9]{2})?)',
            r'amount.*?([0-9,]+(?:\.[0-9]{2})?)'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, contract_text, re.IGNORECASE)
            for match in matches:
                try:
                    # Clean and convert amount
                    amount_str = match.replace(',', '')
                    amount = float(amount_str)
                    if amount > 100:  # Filter out small amounts that might be noise
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Take the largest amount as likely total contract value
        extracted_data["total_value"] = max(amounts) if amounts else 0.0
        
        # Extract payment terms
        terms_patterns = [
            r'Net (\d+)',
            r'(\d+) days?',
            r'payment.*?(\d+).*?days',
            r'due.*?(\d+).*?days',
            r'(30|60|90) days?',
            r'(Net 30|Net 60|Net 90)',
            r'(50%.*?upfront|50%.*?completion)',
            r'(monthly|quarterly|annually)',
        ]
        
        payment_terms = []
        for pattern in terms_patterns:
            matches = re.findall(pattern, contract_text, re.IGNORECASE)
            payment_terms.extend(matches)
        
        # Determine billing terms
        if any('Net' in term for term in payment_terms):
            billing_terms = next(term for term in payment_terms if 'Net' in term)
        elif any('30' in term for term in payment_terms):
            billing_terms = "Net 30"
        elif any('upfront' in term.lower() for term in payment_terms):
            billing_terms = "50% upfront, 50% on completion"
        elif any('monthly' in term.lower() for term in payment_terms):
            billing_terms = "Monthly billing"
        else:
            billing_terms = "Net 30"  # Default
        
        extracted_data["billing_terms"] = billing_terms
        
        # Extract service description
        service_patterns = [
            r'(?:for|provide|services?):\s*([^.]{10,100})',
            r'(?:work|project|deliverable).*?:\s*([^.]{10,100})',
            r'(?:development|design|consulting).*?([^.]{10,100})'
        ]
        
        service_description = "Professional services"  # Default
        for pattern in service_patterns:
            match = re.search(pattern, contract_text, re.IGNORECASE)
            if match:
                service_description = match.group(1).strip()
                break
        
        extracted_data["service_description"] = service_description
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, contract_text, re.IGNORECASE)
            dates.extend(matches)
        
        # Use current date as start date if none found
        extracted_data["contract_start_date"] = dates[0] if dates else datetime.now().strftime("%Y-%m-%d")
        
        # Generate payment schedule based on terms
        if "monthly" in billing_terms.lower():
            payment_schedule = "Monthly invoicing on the 1st of each month"
        elif "50%" in billing_terms.lower():
            payment_schedule = "50% due upon signing, 50% due upon completion"
        else:
            payment_schedule = f"Single payment due {billing_terms.lower()}"
        
        extracted_data["payment_schedule"] = payment_schedule
        
        # Validation and confidence scoring
        confidence_score = 0
        if extracted_data["client_name"] != "Not specified":
            confidence_score += 25
        if extracted_data["contact_email"] != "Not specified":
            confidence_score += 25
        if extracted_data["total_value"] > 0:
            confidence_score += 25
        if billing_terms != "Net 30":  # Default wasn't used
            confidence_score += 25
        
        extracted_data["confidence_score"] = confidence_score
        extracted_data["extraction_quality"] = "high" if confidence_score >= 75 else "medium" if confidence_score >= 50 else "low"
        
        print(f"✅ Contract data extracted with {confidence_score}% confidence")
        print(f"   Client: {extracted_data['client_name']}")
        print(f"   Value: ${extracted_data['total_value']:,.2f}")
        print(f"   Terms: {extracted_data['billing_terms']}")
        
        return json.dumps(extracted_data, indent=2)
        
    except Exception as e:
        error_msg = f"Error extracting contract data: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Fallback with minimal data
        fallback_data = {
            "client_name": "Contract Parsing Failed",
            "contact_email": "Not specified",
            "total_value": 0.0,
            "billing_terms": "Net 30",
            "service_description": "Professional services",
            "contract_start_date": datetime.now().strftime("%Y-%m-%d"),
            "payment_schedule": "Manual review required",
            "confidence_score": 0,
            "extraction_quality": "failed",
            "error": error_msg,
            "data_source": "Fallback - parsing failed"
        }
        
        return json.dumps(fallback_data, indent=2)

@tool("analyze_billing_terms", args_schema=BillingTermsInput)
def analyze_billing_terms(terms_text: str, total_amount: float) -> str:
    """Analyze billing terms to determine payment schedule and invoice timing."""
    try:
        print(f"📋 Analyzing billing terms for ${total_amount:,.2f} contract")
        
        analysis = {
            "total_contract_value": total_amount,
            "analysis_timestamp": datetime.now().isoformat(),
            "terms_analyzed": terms_text,
            "data_source": "Billing Terms Analysis"
        }
        
        terms_lower = terms_text.lower()
        
        # Determine invoice schedule
        if "50%" in terms_text and "upfront" in terms_lower:
            # Split payment structure
            upfront_amount = total_amount * 0.5
            completion_amount = total_amount * 0.5
            
            analysis.update({
                "payment_structure": "split",
                "number_of_invoices": 2,
                "invoice_schedule": [
                    {
                        "invoice_number": 1,
                        "description": "Project initiation - 50% upfront payment",
                        "amount": upfront_amount,
                        "due_date": datetime.now().strftime("%Y-%m-%d"),
                        "timing": "immediate"
                    },
                    {
                        "invoice_number": 2,
                        "description": "Project completion - final 50% payment",
                        "amount": completion_amount,
                        "due_date": "TBD - upon completion",
                        "timing": "completion"
                    }
                ]
            })
            
        elif "monthly" in terms_lower or "month" in terms_lower:
            # Monthly billing structure
            if "12" in terms_text or "annual" in terms_lower:
                months = 12
            elif "6" in terms_text:
                months = 6
            else:
                months = 3  # Default quarterly
            
            monthly_amount = total_amount / months
            
            schedule = []
            for i in range(months):
                due_date = datetime.now() + timedelta(days=30 * i)
                schedule.append({
                    "invoice_number": i + 1,
                    "description": f"Monthly service fee - Month {i + 1}",
                    "amount": monthly_amount,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "timing": f"month_{i + 1}"
                })
            
            analysis.update({
                "payment_structure": "recurring",
                "number_of_invoices": months,
                "monthly_amount": monthly_amount,
                "billing_frequency": "monthly",
                "invoice_schedule": schedule
            })
            
        elif "milestone" in terms_lower or "phase" in terms_lower:
            # Milestone-based billing
            # Assume 3 milestones for simplicity
            milestone_amount = total_amount / 3
            
            schedule = []
            for i in range(3):
                due_date = datetime.now() + timedelta(days=30 * i)
                schedule.append({
                    "invoice_number": i + 1,
                    "description": f"Milestone {i + 1} completion",
                    "amount": milestone_amount,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "timing": f"milestone_{i + 1}"
                })
            
            analysis.update({
                "payment_structure": "milestone",
                "number_of_invoices": 3,
                "milestone_amount": milestone_amount,
                "invoice_schedule": schedule
            })
            
        else:
            # Single payment
            net_days = 30  # Default
            if "net 60" in terms_lower:
                net_days = 60
            elif "net 90" in terms_lower:
                net_days = 90
            elif "net 15" in terms_lower:
                net_days = 15
            
            due_date = datetime.now() + timedelta(days=net_days)
            
            analysis.update({
                "payment_structure": "single",
                "number_of_invoices": 1,
                "net_terms": f"Net {net_days}",
                "invoice_schedule": [{
                    "invoice_number": 1,
                    "description": "Full project payment",
                    "amount": total_amount,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "timing": "immediate_with_terms"
                }]
            })
        
        # Calculate total days to collect all payments
        if analysis.get("invoice_schedule"):
            last_due_date = max([
                datetime.strptime(inv["due_date"], "%Y-%m-%d") 
                for inv in analysis["invoice_schedule"] 
                if inv["due_date"] != "TBD - upon completion"
            ])
            collection_period = (last_due_date - datetime.now()).days
            analysis["total_collection_days"] = max(collection_period, 0)
        
        # Recommendations
        recommendations = []
        if analysis.get("payment_structure") == "split":
            recommendations.append("Create first invoice immediately for upfront payment")
            recommendations.append("Schedule second invoice as draft for completion milestone")
        elif analysis.get("payment_structure") == "recurring":
            recommendations.append("Set up automated monthly invoicing")
            recommendations.append("Configure recurring payment reminders")
        elif analysis.get("payment_structure") == "milestone":
            recommendations.append("Create milestone tracking system")
            recommendations.append("Link invoice generation to project completion status")
        else:
            recommendations.append("Create single invoice with appropriate payment terms")
        
        analysis["recommendations"] = recommendations
        
        print(f"✅ Billing analysis complete:")
        print(f"   Structure: {analysis.get('payment_structure', 'unknown')}")
        print(f"   Invoices: {analysis.get('number_of_invoices', 0)}")
        if analysis.get("monthly_amount"):
            print(f"   Monthly: ${analysis['monthly_amount']:,.2f}")
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        error_msg = f"Error analyzing billing terms: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Fallback analysis
        fallback_analysis = {
            "total_contract_value": total_amount,
            "payment_structure": "single",
            "number_of_invoices": 1,
            "net_terms": "Net 30",
            "invoice_schedule": [{
                "invoice_number": 1,
                "description": "Full project payment",
                "amount": total_amount,
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "timing": "immediate_with_terms"
            }],
            "recommendations": ["Manual review required due to parsing error"],
            "error": error_msg,
            "data_source": "Fallback - analysis failed"
        }
        
        return json.dumps(fallback_analysis, indent=2)

@tool("validate_contract_data", args_schema=BaseModel)
def validate_contract_data(contract_data: str) -> str:
    """Validate extracted contract data for completeness and accuracy."""
    try:
        print("✅ Validating contract data completeness")
        
        # Parse the contract data JSON
        try:
            data = json.loads(contract_data) if isinstance(contract_data, str) else contract_data
        except json.JSONDecodeError:
            return json.dumps({
                "valid": False,
                "errors": ["Invalid JSON format in contract data"],
                "data_source": "Validation Error"
            })
        
        validation_result = {
            "validation_timestamp": datetime.now().isoformat(),
            "data_source": "Contract Data Validation"
        }
        
        errors = []
        warnings = []
        required_fields = ["client_name", "total_value", "billing_terms"]
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field] or data[field] == "Not specified":
                errors.append(f"Missing required field: {field}")
        
        # Validate client name
        if data.get("client_name") and len(data["client_name"]) < 3:
            warnings.append("Client name seems too short")
        
        # Validate email format
        email = data.get("contact_email", "")
        if email and email != "Not specified":
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
            if not re.match(email_pattern, email):
                warnings.append("Email format appears invalid")
        else:
            warnings.append("No contact email provided")
        
        # Validate total value
        total_value = data.get("total_value", 0)
        if total_value <= 0:
            errors.append("Total contract value must be greater than zero")
        elif total_value < 100:
            warnings.append("Total contract value seems unusually low")
        elif total_value > 1000000:
            warnings.append("Total contract value is very high - please verify")
        
        # Validate billing terms
        billing_terms = data.get("billing_terms", "")
        valid_terms = ["net 30", "net 60", "net 90", "50% upfront", "monthly", "quarterly"]
        if not any(term in billing_terms.lower() for term in valid_terms):
            warnings.append("Billing terms format not recognized")
        
        # Overall validation status
        is_valid = len(errors) == 0
        completeness_score = 0
        
        checkable_fields = ["client_name", "contact_email", "total_value", "billing_terms", "service_description"]
        for field in checkable_fields:
            if data.get(field) and data[field] != "Not specified":
                completeness_score += 20
        
        validation_result.update({
            "valid": is_valid,
            "completeness_score": completeness_score,
            "errors": errors,
            "warnings": warnings,
            "ready_for_processing": is_valid and completeness_score >= 60,
            "required_manual_review": len(warnings) > 2 or total_value > 50000
        })
        
        if is_valid:
            print(f"✅ Contract data validation passed ({completeness_score}% complete)")
        else:
            print(f"❌ Contract data validation failed: {len(errors)} errors")
        
        if warnings:
            print(f"⚠️ {len(warnings)} warnings found")
        
        return json.dumps(validation_result, indent=2)
        
    except Exception as e:
        error_msg = f"Error validating contract data: {str(e)}"
        print(f"❌ {error_msg}")
        
        return json.dumps({
            "valid": False,
            "errors": [error_msg],
            "data_source": "Validation Error"
        })

def get_contract_tools():
    """Get all contract processing tools for the agent."""
    return [
        extract_contract_data,
        analyze_billing_terms,
        validate_contract_data
    ]