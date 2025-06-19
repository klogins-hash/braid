"""
SQL database tools for financial forecasting agent.
Handles data storage and retrieval operations.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from database.database import db_manager

logger = logging.getLogger(__name__)

@tool
def store_xero_data_to_sql(xero_data: str, user_id: str = "user_123") -> str:
    """Store Xero financial data in SQL database for historical analysis.
    
    Args:
        xero_data: JSON string containing Xero financial data
        user_id: User identifier for the client
        
    Returns:
        Success confirmation message
    """
    try:
        # Parse Xero data
        if isinstance(xero_data, str):
            try:
                parsed_data = json.loads(xero_data)
            except json.JSONDecodeError:
                # If it's not JSON, treat as raw text data
                parsed_data = {"raw_response": xero_data}
        else:
            parsed_data = xero_data
        
        # Store in database
        success = db_manager.store_historical_data(
            user_id=user_id,
            xero_data=parsed_data,
            report_type="profit_and_loss"
        )
        
        if success:
            logger.info(f"✅ Stored Xero data for {user_id}")
            return f"✅ Successfully stored Xero financial data for {user_id} in SQL database"
        else:
            logger.error(f"❌ Failed to store Xero data for {user_id}")
            return f"❌ Failed to store Xero data in SQL database for {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error storing Xero data: {e}")
        return f"❌ Error storing Xero data: {str(e)}"

@tool  
def get_client_info_from_sql(user_id: str = "user_123") -> str:
    """Retrieve client information from SQL database.
    
    Args:
        user_id: User identifier for the client
        
    Returns:
        Client information in JSON format
    """
    try:
        client_data = db_manager.get_client(user_id)
        
        if client_data:
            logger.info(f"✅ Retrieved client info for {user_id}")
            return json.dumps(client_data, indent=2)
        else:
            logger.warning(f"⚠️ No client data found for {user_id}")
            return f"❌ No client information found for user ID: {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error retrieving client info: {e}")
        return f"❌ Error retrieving client information: {str(e)}"

@tool
def get_historical_data_from_sql(user_id: str = "user_123", limit: int = 5) -> str:
    """Retrieve historical financial data from SQL database.
    
    Args:
        user_id: User identifier for the client
        limit: Maximum number of historical records to retrieve
        
    Returns:
        Historical financial data in JSON format
    """
    try:
        historical_data = db_manager.get_historical_data(user_id, limit)
        
        if historical_data:
            logger.info(f"✅ Retrieved {len(historical_data)} historical records for {user_id}")
            return json.dumps(historical_data, indent=2)
        else:
            logger.warning(f"⚠️ No historical data found for {user_id}")
            return f"❌ No historical financial data found for user ID: {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error retrieving historical data: {e}")
        return f"❌ Error retrieving historical data: {str(e)}"

@tool
def store_forecast_assumptions_sql(assumptions_data: str, user_id: str = "user_123") -> str:
    """Store forecast assumptions in SQL database.
    
    Args:
        assumptions_data: JSON string containing forecast assumptions
        user_id: User identifier for the client
        
    Returns:
        Success confirmation with assumptions ID
    """
    try:
        # Parse assumptions data
        if isinstance(assumptions_data, str):
            try:
                parsed_assumptions = json.loads(assumptions_data)
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON in assumptions data")
                return f"❌ Invalid JSON format in assumptions data"
        else:
            parsed_assumptions = assumptions_data
        
        # Store assumptions
        assumptions_id = db_manager.store_forecast_assumptions(user_id, parsed_assumptions)
        
        if assumptions_id:
            logger.info(f"✅ Stored forecast assumptions for {user_id} with ID {assumptions_id}")
            return f"✅ Successfully stored forecast assumptions for {user_id}. Assumptions ID: {assumptions_id}"
        else:
            logger.error(f"❌ Failed to store assumptions for {user_id}")
            return f"❌ Failed to store forecast assumptions for {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error storing forecast assumptions: {e}")
        return f"❌ Error storing forecast assumptions: {str(e)}"

@tool
def store_forecast_results_sql(forecast_data: str, assumptions_id: str, user_id: str = "user_123") -> str:
    """Store forecast results in SQL database.
    
    Args:
        forecast_data: JSON string containing forecast results
        assumptions_id: ID of the associated assumptions
        user_id: User identifier for the client
        
    Returns:
        Success confirmation message
    """
    try:
        # Parse forecast data
        if isinstance(forecast_data, str):
            try:
                parsed_forecast = json.loads(forecast_data)
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON in forecast data")
                return f"❌ Invalid JSON format in forecast data"
        else:
            parsed_forecast = forecast_data
        
        # Convert assumptions_id to integer
        try:
            assumptions_id_int = int(assumptions_id)
        except (ValueError, TypeError):
            logger.error(f"❌ Invalid assumptions ID: {assumptions_id}")
            return f"❌ Invalid assumptions ID format: {assumptions_id}"
        
        # Ensure forecast data is a list
        if not isinstance(parsed_forecast, list):
            logger.error(f"❌ Forecast data must be a list of yearly projections")
            return f"❌ Forecast data must be a list of yearly projections"
        
        # Store forecast results
        success = db_manager.store_forecast_results(user_id, assumptions_id_int, parsed_forecast)
        
        if success:
            logger.info(f"✅ Stored forecast results for {user_id}")
            return f"✅ Successfully stored forecast results for {user_id} with assumptions ID {assumptions_id}"
        else:
            logger.error(f"❌ Failed to store forecast results for {user_id}")
            return f"❌ Failed to store forecast results for {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error storing forecast results: {e}")
        return f"❌ Error storing forecast results: {str(e)}"

@tool
def approve_forecast_sql(assumptions_id: str, user_id: str = "user_123") -> str:
    """Mark forecast assumptions and results as approved in SQL database.
    
    Args:
        assumptions_id: ID of the assumptions to approve
        user_id: User identifier for the client
        
    Returns:
        Success confirmation message
    """
    try:
        # Convert assumptions_id to integer
        try:
            assumptions_id_int = int(assumptions_id)
        except (ValueError, TypeError):
            logger.error(f"❌ Invalid assumptions ID: {assumptions_id}")
            return f"❌ Invalid assumptions ID format: {assumptions_id}"
        
        # Approve forecast
        success = db_manager.approve_forecast(user_id, assumptions_id_int)
        
        if success:
            logger.info(f"✅ Approved forecast for {user_id}")
            return f"✅ Successfully approved forecast for {user_id} with assumptions ID {assumptions_id}"
        else:
            logger.error(f"❌ Failed to approve forecast for {user_id}")
            return f"❌ Failed to approve forecast for {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error approving forecast: {e}")
        return f"❌ Error approving forecast: {str(e)}"

@tool
def store_notion_report_sql(notion_data: str, assumptions_id: str, user_id: str = "user_123") -> str:
    """Store Notion report information in SQL database.
    
    Args:
        notion_data: JSON string containing Notion report data
        assumptions_id: ID of the associated assumptions
        user_id: User identifier for the client
        
    Returns:
        Success confirmation message
    """
    try:
        # Parse Notion data
        if isinstance(notion_data, str):
            try:
                parsed_notion = json.loads(notion_data)
            except json.JSONDecodeError:
                # If not JSON, treat as simple text
                parsed_notion = {"content": notion_data}
        else:
            parsed_notion = notion_data
        
        # Convert assumptions_id to integer
        try:
            assumptions_id_int = int(assumptions_id)
        except (ValueError, TypeError):
            logger.error(f"❌ Invalid assumptions ID: {assumptions_id}")
            return f"❌ Invalid assumptions ID format: {assumptions_id}"
        
        # Store Notion report
        success = db_manager.store_notion_report(user_id, assumptions_id_int, parsed_notion)
        
        if success:
            logger.info(f"✅ Stored Notion report for {user_id}")
            return f"✅ Successfully stored Notion report for {user_id}"
        else:
            logger.error(f"❌ Failed to store Notion report for {user_id}")
            return f"❌ Failed to store Notion report for {user_id}"
            
    except Exception as e:
        logger.error(f"❌ Error storing Notion report: {e}")
        return f"❌ Error storing Notion report: {str(e)}"