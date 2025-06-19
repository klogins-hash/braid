"""
CSV processing tools for customer data analysis.
"""

import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime


class CustomerDataAnalyzer:
    """Tools for analyzing customer data from CSV files."""
    
    @staticmethod
    def load_customer_data(file_path: str) -> Dict[str, Any]:
        """Load customer data from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with loaded data and metadata
        """
        try:
            df = pd.read_csv(file_path)
            
            return {
                "success": True,
                "data": df.to_dict('records'),
                "metadata": {
                    "total_rows": len(df),
                    "columns": list(df.columns),
                    "file_size": Path(file_path).stat().st_size,
                    "loaded_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metadata": {"loaded_at": datetime.now().isoformat()}
            }
    
    @staticmethod
    def analyze_customer_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze customer metrics from loaded data.
        
        Args:
            data: List of customer records
            
        Returns:
            Analysis results and metrics
        """
        if not data:
            return {"error": "No data provided for analysis"}
        
        df = pd.DataFrame(data)
        
        # Basic statistics
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        analysis = {
            "total_customers": len(df),
            "data_quality": {
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_rows": df.duplicated().sum(),
                "completeness_percentage": ((df.count() / len(df)) * 100).to_dict()
            }
        }
        
        # Numeric analysis
        if len(numeric_columns) > 0:
            analysis["numeric_metrics"] = {
                column: {
                    "mean": float(df[column].mean()) if not df[column].isnull().all() else None,
                    "median": float(df[column].median()) if not df[column].isnull().all() else None,
                    "std": float(df[column].std()) if not df[column].isnull().all() else None,
                    "min": float(df[column].min()) if not df[column].isnull().all() else None,
                    "max": float(df[column].max()) if not df[column].isnull().all() else None
                }
                for column in numeric_columns
            }
        
        # Categorical analysis
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            analysis["categorical_metrics"] = {}
            for column in categorical_columns:
                value_counts = df[column].value_counts()
                analysis["categorical_metrics"][column] = {
                    "unique_values": int(df[column].nunique()),
                    "most_common": value_counts.head().to_dict(),
                    "distribution": value_counts.to_dict()
                }
        
        return analysis
    
    @staticmethod
    def get_customer_profile(
        data: List[Dict[str, Any]], 
        customer_id: str,
        id_column: str = "customer_id"
    ) -> Dict[str, Any]:
        """Get detailed profile for a specific customer.
        
        Args:
            data: Customer data records
            customer_id: ID of customer to profile
            id_column: Name of the ID column
            
        Returns:
            Customer profile and history
        """
        df = pd.DataFrame(data)
        
        if id_column not in df.columns:
            return {"error": f"Column '{id_column}' not found in data"}
        
        customer_data = df[df[id_column] == customer_id]
        
        if customer_data.empty:
            return {"error": f"Customer '{customer_id}' not found"}
        
        # Get customer record (assuming one row per customer)
        customer_record = customer_data.iloc[0].to_dict()
        
        # Calculate customer metrics
        profile = {
            "customer_id": customer_id,
            "profile": customer_record,
            "metrics": {},
            "insights": []
        }
        
        # Add calculated metrics
        numeric_columns = customer_data.select_dtypes(include=['number']).columns
        for column in numeric_columns:
            if not pd.isna(customer_record.get(column)):
                profile["metrics"][column] = {
                    "value": customer_record[column],
                    "percentile": float((df[column] < customer_record[column]).mean() * 100)
                }
        
        # Generate insights
        if "satisfaction_score" in customer_record:
            score = customer_record["satisfaction_score"]
            if score >= 4.5:
                profile["insights"].append("High satisfaction - excellent retention candidate")
            elif score <= 3.0:
                profile["insights"].append("Low satisfaction - requires attention")
        
        if "ticket_count" in customer_record:
            tickets = customer_record["ticket_count"]
            if tickets > df["ticket_count"].quantile(0.9):
                profile["insights"].append("High support usage - consider proactive outreach")
        
        return profile
    
    @staticmethod
    def export_analysis_report(
        analysis: Dict[str, Any], 
        output_path: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export analysis results to file.
        
        Args:
            analysis: Analysis results to export
            output_path: Path for output file
            format: Export format (json, csv)
            
        Returns:
            Export operation result
        """
        try:
            output_path = Path(output_path)
            
            if format.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
            
            elif format.lower() == "csv":
                # Convert to flat structure for CSV export
                flat_data = []
                if "numeric_metrics" in analysis:
                    for metric, values in analysis["numeric_metrics"].items():
                        flat_data.append({
                            "metric_type": "numeric",
                            "metric_name": metric,
                            **values
                        })
                
                if flat_data:
                    df = pd.DataFrame(flat_data)
                    df.to_csv(output_path, index=False)
                else:
                    return {"success": False, "error": "No numeric data to export as CSV"}
            
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            return {
                "success": True,
                "output_file": str(output_path),
                "file_size": output_path.stat().st_size,
                "format": format
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class TicketAnalyzer:
    """Tools for analyzing support ticket data."""
    
    @staticmethod
    def analyze_ticket_trends(tickets_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze support ticket trends and patterns.
        
        Args:
            tickets_data: List of ticket records
            
        Returns:
            Trend analysis results
        """
        if not tickets_data:
            return {"error": "No ticket data provided"}
        
        df = pd.DataFrame(tickets_data)
        
        analysis = {
            "total_tickets": len(df),
            "status_distribution": {},
            "priority_distribution": {},
            "resolution_metrics": {}
        }
        
        # Status distribution
        if "status" in df.columns:
            analysis["status_distribution"] = df["status"].value_counts().to_dict()
        
        # Priority distribution
        if "priority" in df.columns:
            analysis["priority_distribution"] = df["priority"].value_counts().to_dict()
        
        # Resolution time analysis (if available)
        if "created_at" in df.columns and "resolved_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["resolved_at"] = pd.to_datetime(df["resolved_at"])
            
            resolved_tickets = df.dropna(subset=["resolved_at"])
            if not resolved_tickets.empty:
                resolution_times = (resolved_tickets["resolved_at"] - resolved_tickets["created_at"]).dt.total_seconds() / 3600  # hours
                
                analysis["resolution_metrics"] = {
                    "average_resolution_hours": float(resolution_times.mean()),
                    "median_resolution_hours": float(resolution_times.median()),
                    "fastest_resolution_hours": float(resolution_times.min()),
                    "slowest_resolution_hours": float(resolution_times.max())
                }
        
        return analysis