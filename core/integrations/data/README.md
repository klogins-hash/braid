# MongoDB Direct API Integration

Direct API integration for MongoDB operations and Atlas management, providing comprehensive database functionality without MCP server dependencies.

## 🚀 Features

### Core Database Operations (CRUD)
- **Find**: Query documents with filtering, projection, and sorting
- **Insert**: Insert single or multiple documents with bulk operations
- **Update**: Update documents with atomic operations and upserts
- **Delete**: Remove documents with precise filtering
- **Aggregate**: Complex data processing with aggregation pipelines

### Database Administration
- **List Databases**: View all databases with size and collection info
- **List Collections**: View collections with document counts and indexes
- **Create Indexes**: Optimize query performance with custom indexes
- **Collection Stats**: Detailed collection statistics and metrics
- **Drop Collections**: Remove collections safely

### MongoDB Atlas Management
- **List Clusters**: View Atlas clusters in projects
- **Create Clusters**: Deploy new Atlas clusters with custom configurations
- **List Projects**: Manage Atlas projects and organizations

## 📋 Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```bash
# Required: MongoDB Connection
MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/database

# Optional: Atlas API (for cluster management)
MONGODB_ATLAS_API_CLIENT_ID=your-atlas-client-id
MONGODB_ATLAS_API_CLIENT_SECRET=your-atlas-client-secret

# Optional: Security Settings
MDB_MCP_READ_ONLY=false
MDB_MCP_DISABLED_TOOLS=drop_collection,atlas_create_cluster
```

### 2. MongoDB Connection Options

#### Option 1: Local MongoDB
```bash
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/mydatabase
```

#### Option 2: MongoDB Atlas
```bash
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database
```

#### Option 3: Self-Hosted MongoDB
```bash
MONGODB_CONNECTION_STRING=mongodb://user:pass@host:port/database
```

### 3. Atlas API Setup (Optional)

For Atlas cluster management:

1. **Create Service Account**:
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Navigate to Access Manager → Service Accounts
   - Create new service account with required permissions

2. **Generate API Keys**:
   - Create API keys for the service account
   - Copy Client ID and Secret

### 4. Install Dependencies

```bash
pip install pymongo requests python-dotenv
```

## 🔧 Usage Examples

### Basic CRUD Operations

```python
from core.integrations.mongodb.tools import (
    mongo_find, mongo_insert, mongo_update, mongo_delete
)

# Insert documents
insert_result = mongo_insert.invoke({
    "database": "myapp",
    "collection": "users",
    "documents": [
        {"name": "John Doe", "email": "john@example.com", "age": 30},
        {"name": "Jane Smith", "email": "jane@example.com", "age": 25}
    ]
})

# Find documents
find_result = mongo_find.invoke({
    "database": "myapp",
    "collection": "users",
    "query": {"age": {"$gte": 25}},
    "projection": {"name": 1, "email": 1},
    "sort": {"name": 1},
    "limit": 10
})

# Update documents
update_result = mongo_update.invoke({
    "database": "myapp",
    "collection": "users",
    "filter": {"name": "John Doe"},
    "update": {"$set": {"age": 31}},
    "upsert": False
})

# Delete documents
delete_result = mongo_delete.invoke({
    "database": "myapp",
    "collection": "users",
    "filter": {"age": {"$lt": 18}},
    "multi": True
})
```

### Aggregation Operations

```python
from core.integrations.mongodb.tools import mongo_aggregate

# Complex aggregation pipeline
aggregation_result = mongo_aggregate.invoke({
    "database": "ecommerce",
    "collection": "orders",
    "pipeline": [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer_id",
            "total_spent": {"$sum": "$amount"},
            "order_count": {"$sum": 1}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 10}
    ]
})
```

### Database Administration

```python
from core.integrations.mongodb.tools import (
    mongo_list_databases, mongo_list_collections, 
    mongo_create_index, mongo_get_collection_stats
)

# List all databases
databases = mongo_list_databases.invoke({})

# List collections in database
collections = mongo_list_collections.invoke({
    "database": "myapp"
})

# Create index for performance
index_result = mongo_create_index.invoke({
    "database": "myapp",
    "collection": "users",
    "keys": {"email": 1},
    "options": {"unique": True}
})

# Get collection statistics
stats = mongo_get_collection_stats.invoke({
    "database": "myapp",
    "collection": "users"
})
```

### Atlas Management

```python
from core.integrations.mongodb.tools import (
    mongo_atlas_list_projects, mongo_atlas_list_clusters,
    mongo_atlas_create_cluster
)

# List Atlas projects
projects = mongo_atlas_list_projects.invoke({})

# List clusters in project
clusters = mongo_atlas_list_clusters.invoke({
    "project_id": "60f7b1a5b4b1234567890123"
})

# Create new cluster
new_cluster = mongo_atlas_create_cluster.invoke({
    "project_id": "60f7b1a5b4b1234567890123",
    "cluster_name": "my-new-cluster",
    "cluster_config": {
        "clusterType": "REPLICASET",
        "providerSettings": {
            "providerName": "AWS",
            "instanceSizeName": "M10",
            "regionName": "US_EAST_1"
        }
    }
})
```

### Agent Integration

```python
from core.integrations.mongodb.tools import (
    get_mongodb_tools, get_mongodb_crud_tools
)
from langchain_openai import ChatOpenAI

# Get all MongoDB tools
all_tools = get_mongodb_tools()

# Or get specific tool sets
crud_tools = get_mongodb_crud_tools()      # Only CRUD operations
admin_tools = get_mongodb_admin_tools()    # Database administration
atlas_tools = get_mongodb_atlas_tools()   # Atlas management

# Use in LangGraph agent
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_with_tools = llm.bind_tools(all_tools)
```

## 🔍 Tool Reference

### CRUD Operations
- `mongo_find()` - Query documents with filtering and projection
- `mongo_insert()` - Insert single or multiple documents
- `mongo_update()` - Update documents with atomic operations
- `mongo_delete()` - Delete documents with filtering
- `mongo_aggregate()` - Complex aggregation pipelines

### Database Administration
- `mongo_list_databases()` - List all databases with metadata
- `mongo_list_collections()` - List collections in database
- `mongo_create_index()` - Create performance indexes
- `mongo_get_collection_stats()` - Detailed collection statistics
- `mongo_drop_collection()` - Remove collections (use with caution)

### Atlas Management
- `mongo_atlas_list_projects()` - List Atlas projects
- `mongo_atlas_list_clusters()` - List clusters in project
- `mongo_atlas_create_cluster()` - Create new Atlas clusters

### Tool Collections
- `get_mongodb_tools()` - All MongoDB tools
- `get_mongodb_crud_tools()` - CRUD operations only
- `get_mongodb_admin_tools()` - Administration tools only
- `get_mongodb_atlas_tools()` - Atlas management only

## 🔒 Security Best Practices

1. **Connection Security**: Use SSL/TLS connections and strong authentication
2. **Least Privilege**: Grant minimal required database permissions
3. **Environment Variables**: Never hardcode connection strings
4. **Network Security**: Use VPC/firewall rules to restrict access
5. **Read-Only Mode**: Use `MDB_MCP_READ_ONLY=true` for analysis agents
6. **Tool Filtering**: Disable dangerous operations with `MDB_MCP_DISABLED_TOOLS`

## 🚨 Error Handling

All tools return JSON responses with clear error information:

```json
{
  "error": true,
  "message": "Connection failed: authentication error"
}
```

Successful responses include operation details:

```json
{
  "success": true,
  "database": "myapp",
  "collection": "users", 
  "count": 5,
  "documents": [...]
}
```

## ⚡ Performance Tips

1. **Use Indexes**: Create indexes for frequently queried fields
2. **Projection**: Only select needed fields to reduce data transfer
3. **Limit Results**: Use reasonable limits for large collections
4. **Aggregation**: Use aggregation pipelines for complex data processing
5. **Connection Pooling**: PyMongo automatically handles connection pooling

## 💰 Cost Considerations

### MongoDB Atlas
- **Cluster Size**: Choose appropriate instance sizes (M10, M20, etc.)
- **Region Selection**: Consider data locality and transfer costs
- **Storage**: Monitor data size and indexes
- **Operations**: Free tier includes limited operations

### Self-Hosted
- **Server Resources**: CPU and memory requirements scale with usage
- **Storage**: SSD recommended for better performance
- **Network**: Consider bandwidth for large data transfers

## 📚 Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Aggregation Pipeline](https://docs.mongodb.com/manual/aggregation/)

## 🔄 Migration from MCP

This integration provides the same functionality as the MongoDB MCP server:

**Before (MCP)**:
```bash
npx mongodb-mcp-server
```

**After (Direct Integration)**:
```python
from core.integrations.mongodb.tools import get_mongodb_tools
tools = get_mongodb_tools()
```

All tool names and functionality remain consistent for easy migration.