"""
MongoDB Direct API Integration Tools

Provides direct access to MongoDB operations and Atlas management
without MCP server dependencies.
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from urllib.parse import quote_plus

from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

try:
    import pymongo
    from pymongo import MongoClient
    import requests
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        "MongoDB tools require additional dependencies. "
        "Install with: pip install pymongo requests python-dotenv"
    )

# Load environment variables
load_dotenv(override=True)

# --- Input Schemas ---

class MongoFindInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query filter")
    projection: Optional[Dict[str, Any]] = Field(default=None, description="Field projection")
    limit: Optional[int] = Field(default=100, description="Maximum number of documents to return")
    sort: Optional[Dict[str, Any]] = Field(default=None, description="Sort specification")

class MongoInsertInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    documents: List[Dict[str, Any]] = Field(description="Documents to insert")

class MongoUpdateInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    filter: Dict[str, Any] = Field(description="Update filter")
    update: Dict[str, Any] = Field(description="Update operations")
    upsert: bool = Field(default=False, description="Create document if not found")
    multi: bool = Field(default=False, description="Update multiple documents")

class MongoDeleteInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    filter: Dict[str, Any] = Field(description="Deletion filter")
    multi: bool = Field(default=False, description="Delete multiple documents")

class MongoAggregateInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    pipeline: List[Dict[str, Any]] = Field(description="Aggregation pipeline")

class MongoIndexInput(BaseModel):
    database: str = Field(description="Database name")
    collection: str = Field(description="Collection name")
    keys: Dict[str, Any] = Field(description="Index specification")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Index options")

class AtlasClusterInput(BaseModel):
    project_id: str = Field(description="Atlas project ID")
    cluster_name: Optional[str] = Field(default=None, description="Cluster name")

# --- Helper Functions ---

def _get_mongo_client() -> MongoClient:
    """Get MongoDB client connection."""
    # Force reload environment variables
    load_dotenv(override=True)
    
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "").strip()
    if not connection_string:
        raise ValueError(
            "MONGODB_CONNECTION_STRING environment variable not set. "
            "Set it to your MongoDB connection URI."
        )
    
    try:
        print(f"🔄 Connecting to MongoDB...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ SUCCESS! Connected to MongoDB")
        return client
        
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")

def _get_atlas_auth() -> Dict[str, str]:
    """Get Atlas API authentication headers."""
    load_dotenv(override=True)
    
    client_id = os.getenv("MONGODB_ATLAS_API_CLIENT_ID", "").strip()
    client_secret = os.getenv("MONGODB_ATLAS_API_CLIENT_SECRET", "").strip()
    
    if not client_id or not client_secret:
        raise ValueError(
            "Missing Atlas API credentials. Set MONGODB_ATLAS_API_CLIENT_ID "
            "and MONGODB_ATLAS_API_CLIENT_SECRET environment variables."
        )
    
    # Create Basic Auth header
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    return {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }

def _make_atlas_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make authenticated request to Atlas API."""
    
    try:
        headers = _get_atlas_auth()
        base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        print(f"🔄 Making Atlas API call: {method} {endpoint}")
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"📊 Atlas API Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS! Atlas API call completed")
            return response.json()
        else:
            error_data = response.json() if response.content else {}
            return {
                "error": True,
                "status_code": response.status_code,
                "message": error_data.get("detail", f"Atlas API error: {response.status_code}")
            }
            
    except Exception as e:
        print(f"❌ Atlas API Error: {e}")
        return {
            "error": True,
            "message": f"Request failed: {str(e)}"
        }

def _serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format."""
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                result[key] = str(value)  # Convert ObjectId to string
            elif isinstance(value, dict):
                result[key] = _serialize_mongo_doc(value)
            elif isinstance(value, list):
                result[key] = [_serialize_mongo_doc(item) for item in value]
            elif hasattr(value, 'isoformat'):  # DateTime objects
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    elif isinstance(doc, list):
        return [_serialize_mongo_doc(item) for item in doc]
    else:
        return doc

# --- Core CRUD Operations ---

@tool("mongo_find", args_schema=MongoFindInput)
def mongo_find(
    database: str,
    collection: str,
    query: Optional[Dict[str, Any]] = None,
    projection: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    sort: Optional[Dict[str, Any]] = None
) -> str:
    """
    Query documents in MongoDB collection with filtering and projection.
    
    Args:
        database: Database name
        collection: Collection name
        query: Query filter (default: {} for all documents)
        projection: Field projection (default: None for all fields)
        limit: Maximum documents to return (default: 100)
        sort: Sort specification (e.g., {"field": 1} for ascending)
    
    Returns:
        JSON string with matching documents
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        if query is None:
            query = {}
        
        # Build cursor
        cursor = coll.find(query, projection)
        
        if sort:
            cursor = cursor.sort(list(sort.items()))
        
        cursor = cursor.limit(limit)
        
        # Get results
        documents = list(cursor)
        serialized_docs = _serialize_mongo_doc(documents)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "query": query,
            "count": len(documents),
            "documents": serialized_docs
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Find operation failed: {str(e)}"
        })

@tool("mongo_insert", args_schema=MongoInsertInput)
def mongo_insert(
    database: str,
    collection: str,
    documents: List[Dict[str, Any]]
) -> str:
    """
    Insert one or multiple documents into MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
        documents: List of documents to insert
    
    Returns:
        JSON string with insertion results and generated IDs
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        if len(documents) == 1:
            result = coll.insert_one(documents[0])
            inserted_ids = [str(result.inserted_id)]
        else:
            result = coll.insert_many(documents)
            inserted_ids = [str(id_) for id_ in result.inserted_ids]
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "inserted_count": len(inserted_ids),
            "inserted_ids": inserted_ids
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Insert operation failed: {str(e)}"
        })

@tool("mongo_update", args_schema=MongoUpdateInput)
def mongo_update(
    database: str,
    collection: str,
    filter: Dict[str, Any],
    update: Dict[str, Any],
    upsert: bool = False,
    multi: bool = False
) -> str:
    """
    Update documents in MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
        filter: Update filter to match documents
        update: Update operations (e.g., {"$set": {"field": "value"}})
        upsert: Create document if not found (default: False)
        multi: Update multiple documents (default: False)
    
    Returns:
        JSON string with update results and affected count
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        if multi:
            result = coll.update_many(filter, update, upsert=upsert)
        else:
            result = coll.update_one(filter, update, upsert=upsert)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Update operation failed: {str(e)}"
        })

@tool("mongo_delete", args_schema=MongoDeleteInput)
def mongo_delete(
    database: str,
    collection: str,
    filter: Dict[str, Any],
    multi: bool = False
) -> str:
    """
    Delete documents from MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
        filter: Deletion filter to match documents
        multi: Delete multiple documents (default: False)
    
    Returns:
        JSON string with deletion results and count
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        if multi:
            result = coll.delete_many(filter)
        else:
            result = coll.delete_one(filter)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "deleted_count": result.deleted_count
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Delete operation failed: {str(e)}"
        })

@tool("mongo_aggregate", args_schema=MongoAggregateInput)
def mongo_aggregate(
    database: str,
    collection: str,
    pipeline: List[Dict[str, Any]]
) -> str:
    """
    Perform aggregation operations on MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
        pipeline: Aggregation pipeline stages
    
    Returns:
        JSON string with aggregation results
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        result = list(coll.aggregate(pipeline))
        serialized_result = _serialize_mongo_doc(result)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "pipeline": pipeline,
            "result_count": len(result),
            "results": serialized_result
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Aggregation operation failed: {str(e)}"
        })

# --- Database Administration ---

@tool("mongo_list_databases")
def mongo_list_databases() -> str:
    """
    List all databases in the MongoDB instance.
    
    Returns:
        JSON string with database names and sizes
    """
    
    try:
        client = _get_mongo_client()
        db_list = client.list_database_names()
        
        # Get detailed info
        databases = []
        for db_name in db_list:
            try:
                stats = client[db_name].command("dbStats")
                databases.append({
                    "name": db_name,
                    "size_on_disk": stats.get("dataSize", 0),
                    "collections": stats.get("collections", 0),
                    "indexes": stats.get("indexes", 0)
                })
            except:
                databases.append({"name": db_name})
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database_count": len(databases),
            "databases": databases
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"List databases failed: {str(e)}"
        })

@tool("mongo_list_collections")
def mongo_list_collections(database: str) -> str:
    """
    List all collections in a specific database.
    
    Args:
        database: Database name
    
    Returns:
        JSON string with collection names and info
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        
        collection_names = db.list_collection_names()
        
        # Get collection stats
        collections = []
        for coll_name in collection_names:
            try:
                stats = db.command("collStats", coll_name)
                collections.append({
                    "name": coll_name,
                    "document_count": stats.get("count", 0),
                    "size": stats.get("size", 0),
                    "indexes": stats.get("nindexes", 0)
                })
            except:
                collections.append({"name": coll_name})
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection_count": len(collections),
            "collections": collections
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"List collections failed: {str(e)}"
        })

@tool("mongo_create_index", args_schema=MongoIndexInput)
def mongo_create_index(
    database: str,
    collection: str,
    keys: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create index on MongoDB collection for query optimization.
    
    Args:
        database: Database name
        collection: Collection name
        keys: Index specification (e.g., {"field": 1} for ascending)
        options: Index options (e.g., {"unique": True})
    
    Returns:
        JSON string with index creation result
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        coll = db[collection]
        
        if options is None:
            options = {}
        
        # Create index
        index_name = coll.create_index(list(keys.items()), **options)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "index_name": index_name,
            "keys": keys,
            "options": options
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Create index failed: {str(e)}"
        })

@tool("mongo_get_collection_stats")
def mongo_get_collection_stats(database: str, collection: str) -> str:
    """
    Get detailed statistics for a MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
    
    Returns:
        JSON string with collection statistics
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        
        stats = db.command("collStats", collection)
        serialized_stats = _serialize_mongo_doc(stats)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "stats": serialized_stats
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Get collection stats failed: {str(e)}"
        })

@tool("mongo_drop_collection")
def mongo_drop_collection(database: str, collection: str) -> str:
    """
    Drop (delete) a MongoDB collection.
    
    Args:
        database: Database name
        collection: Collection name
    
    Returns:
        JSON string with operation result
    """
    
    try:
        client = _get_mongo_client()
        db = client[database]
        
        db.drop_collection(collection)
        
        client.close()
        
        return json.dumps({
            "success": True,
            "database": database,
            "collection": collection,
            "message": "Collection dropped successfully"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Drop collection failed: {str(e)}"
        })

# --- Atlas Management ---

@tool("mongo_atlas_list_clusters", args_schema=AtlasClusterInput)
def mongo_atlas_list_clusters(project_id: str) -> str:
    """
    List MongoDB Atlas clusters in a project.
    
    Args:
        project_id: Atlas project ID
    
    Returns:
        JSON string with cluster information
    """
    
    result = _make_atlas_request("GET", f"groups/{project_id}/clusters")
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    clusters = result.get("results", [])
    
    return json.dumps({
        "success": True,
        "project_id": project_id,
        "cluster_count": len(clusters),
        "clusters": clusters
    }, indent=2)

@tool("mongo_atlas_create_cluster")
def mongo_atlas_create_cluster(
    project_id: str,
    cluster_name: str,
    cluster_config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create new MongoDB Atlas cluster.
    
    Args:
        project_id: Atlas project ID
        cluster_name: Name for the new cluster
        cluster_config: Cluster configuration options
    
    Returns:
        JSON string with cluster creation result
    """
    
    if cluster_config is None:
        cluster_config = {
            "name": cluster_name,
            "clusterType": "REPLICASET",
            "providerSettings": {
                "providerName": "AWS",
                "instanceSizeName": "M10",
                "regionName": "US_EAST_1"
            }
        }
    else:
        cluster_config["name"] = cluster_name
    
    result = _make_atlas_request("POST", f"groups/{project_id}/clusters", cluster_config)
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    return json.dumps({
        "success": True,
        "project_id": project_id,
        "cluster_name": cluster_name,
        "cluster_id": result.get("id"),
        "state": result.get("stateName")
    }, indent=2)

@tool("mongo_atlas_list_projects")
def mongo_atlas_list_projects() -> str:
    """
    List MongoDB Atlas projects.
    
    Returns:
        JSON string with project information
    """
    
    result = _make_atlas_request("GET", "groups")
    
    if result.get("error"):
        return json.dumps({
            "error": True,
            "message": result.get("message")
        })
    
    projects = result.get("results", [])
    
    return json.dumps({
        "success": True,
        "project_count": len(projects),
        "projects": projects
    }, indent=2)

# --- Tool Collections ---

def get_mongodb_tools():
    """Get all MongoDB tools."""
    return [
        mongo_find,
        mongo_insert,
        mongo_update,
        mongo_delete,
        mongo_aggregate,
        mongo_list_databases,
        mongo_list_collections,
        mongo_create_index,
        mongo_get_collection_stats,
        mongo_drop_collection,
        mongo_atlas_list_clusters,
        mongo_atlas_create_cluster,
        mongo_atlas_list_projects
    ]

def get_mongodb_crud_tools():
    """Get CRUD operation tools only."""
    return [
        mongo_find,
        mongo_insert,
        mongo_update,
        mongo_delete,
        mongo_aggregate
    ]

def get_mongodb_admin_tools():
    """Get database administration tools."""
    return [
        mongo_list_databases,
        mongo_list_collections,
        mongo_create_index,
        mongo_get_collection_stats,
        mongo_drop_collection
    ]

def get_mongodb_atlas_tools():
    """Get Atlas management tools."""
    return [
        mongo_atlas_list_clusters,
        mongo_atlas_create_cluster,
        mongo_atlas_list_projects
    ]