# MongoDB MCP Server

MongoDB MCP provides comprehensive database operations and MongoDB Atlas cluster management through the Model Context Protocol, enabling AI agents to interact with MongoDB databases and perform data operations.

## Overview

The MongoDB MCP Server is an official implementation from MongoDB that provides secure, controlled access to MongoDB databases and Atlas clusters. It supports both direct database operations and Atlas cloud management functionality.

## Capabilities

### Core Database Operations

- **`mongo_find`**: Query documents with flexible filtering and projection
  - Input: Database, collection, query filter, projection options
  - Output: Matching documents with specified fields
  - Supports: Complex queries, sorting, limiting, field selection

- **`mongo_insert`**: Insert single or multiple documents
  - Input: Database, collection, array of documents
  - Output: Insertion results with generated IDs
  - Features: Bulk insertion, automatic ID generation

- **`mongo_update`**: Update existing documents
  - Input: Database, collection, filter, update operations
  - Output: Update results and affected document count
  - Supports: Update operators, upsert operations

- **`mongo_delete`**: Remove documents from collections
  - Input: Database, collection, deletion filter
  - Output: Deletion results and count
  - Features: Single or multiple document deletion

- **`mongo_aggregate`**: Perform complex data aggregation
  - Input: Database, collection, aggregation pipeline
  - Output: Aggregated results
  - Supports: Full MongoDB aggregation framework

### Database Administration

- **`mongo_list_databases`**: List all available databases
- **`mongo_list_collections`**: List collections in a database
- **`mongo_create_index`**: Create indexes for query optimization
- **`mongo_get_collection_stats`**: Get collection statistics and metrics
- **`mongo_rename_collection`**: Rename collections
- **`mongo_drop_collection`**: Delete collections

### MongoDB Atlas Management

- **`mongo_atlas_list_clusters`**: List Atlas clusters in a project
- **`mongo_atlas_create_cluster`**: Create new Atlas clusters
- **`mongo_atlas_list_projects`**: List Atlas projects
- **`mongo_atlas_create_project`**: Create new Atlas projects
- **`mongo_atlas_list_organizations`**: List Atlas organizations

## Setup Instructions

### Authentication Options

#### Option 1: Direct MongoDB Connection

For direct database access (local MongoDB, self-hosted, or Atlas with connection string):

```bash
# Set your MongoDB connection string
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/mydb
# Or for Atlas:
MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/mydb
```

#### Option 2: MongoDB Atlas API

For Atlas cluster management and operations:

1. **Create Atlas Service Account**:
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Navigate to Access Manager → Service Accounts
   - Create a new service account
   - Generate API keys

2. **Set Environment Variables**:
```bash
MONGODB_ATLAS_API_CLIENT_ID=your-atlas-api-client-id
MONGODB_ATLAS_API_CLIENT_SECRET=your-atlas-api-client-secret
```

### Environment Configuration

Add to your `.env` file:

```bash
# Option 1: Direct Connection
MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/database

# Option 2: Atlas API (for cluster management)
MONGODB_ATLAS_API_CLIENT_ID=your-atlas-api-client-id
MONGODB_ATLAS_API_CLIENT_SECRET=your-atlas-api-client-secret

# Security Options (optional)
MDB_MCP_READ_ONLY=false
MDB_MCP_DISABLED_TOOLS=
MDB_MCP_TELEMETRY_DISABLED=false
```

### Installation

The MCP server is automatically installed when using Braid's Docker orchestration:

```bash
braid package --production
docker compose up --build
```

For manual installation:
```bash
npx -y mongodb-mcp-server
```

## Usage Examples

### Basic CRUD Operations

```python
# Find documents
users = agent.mongo_find(
    database="myapp",
    collection="users",
    query={"status": "active"},
    projection={"name": 1, "email": 1}
)

# Insert new document
result = agent.mongo_insert(
    database="myapp",
    collection="users",
    documents=[{
        "name": "John Doe",
        "email": "john@example.com",
        "status": "active",
        "created_at": "2024-01-01"
    }]
)

# Update documents
update_result = agent.mongo_update(
    database="myapp",
    collection="users",
    filter={"email": "john@example.com"},
    update={"$set": {"status": "premium"}}
)

# Delete documents
delete_result = agent.mongo_delete(
    database="myapp",
    collection="users",
    filter={"status": "inactive"}
)
```

### Advanced Queries and Aggregation

```python
# Complex find with sorting and limiting
top_users = agent.mongo_find(
    database="analytics",
    collection="user_activity",
    query={
        "last_login": {"$gte": "2024-01-01"},
        "subscription": {"$in": ["premium", "enterprise"]}
    },
    projection={"user_id": 1, "activity_score": 1},
    options={
        "sort": {"activity_score": -1},
        "limit": 10
    }
)

# Aggregation pipeline for analytics
monthly_stats = agent.mongo_aggregate(
    database="analytics",
    collection="events",
    pipeline=[
        {"$match": {"event_type": "purchase"}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
            "total_sales": {"$sum": "$amount"},
            "transaction_count": {"$sum": 1},
            "avg_transaction": {"$avg": "$amount"}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 12}
    ]
)
```

### Database Administration

```python
# List all databases
databases = agent.mongo_list_databases()

# List collections in a database
collections = agent.mongo_list_collections(database="myapp")

# Create index for performance
index_result = agent.mongo_create_index(
    database="myapp",
    collection="users",
    keys={"email": 1},
    options={"unique": True, "name": "email_unique_idx"}
)

# Get collection statistics
stats = agent.mongo_get_collection_stats(
    database="myapp",
    collection="users"
)
print(f"Document count: {stats['count']}")
print(f"Storage size: {stats['storageSize']} bytes")
```

### MongoDB Atlas Management

```python
# List Atlas projects
projects = agent.mongo_atlas_list_projects()

# List clusters in a project
clusters = agent.mongo_atlas_list_clusters(projectId="60b8b1234567890abcdef123")

# Create a new Atlas cluster
new_cluster = agent.mongo_atlas_create_cluster(
    projectId="60b8b1234567890abcdef123",
    clusterConfig={
        "name": "MyCluster",
        "clusterType": "REPLICASET",
        "replicationSpecs": [{
            "numShards": 1,
            "regionsConfig": {
                "US_EAST_1": {
                    "electableNodes": 3,
                    "priority": 7,
                    "readOnlyNodes": 0
                }
            }
        }]
    }
)
```

## Use Cases

### Application Development
- **User Management**: Store and manage user profiles, authentication data
- **Content Management**: Handle articles, media metadata, user-generated content
- **E-commerce**: Product catalogs, order management, inventory tracking
- **IoT Data**: Sensor data collection, device management, time-series analytics

### Data Analytics
- **Business Intelligence**: Aggregate sales data, user behavior analytics
- **Reporting**: Generate monthly/quarterly reports from operational data
- **A/B Testing**: Store and analyze experiment results and user segments
- **Performance Monitoring**: Application metrics, error tracking, log analysis

### Database Administration
- **Schema Management**: Create and modify collections, manage indexes
- **Data Migration**: Move data between environments, transform data structures
- **Backup Operations**: Export collections, create data snapshots
- **Performance Optimization**: Monitor query performance, optimize indexes

### MongoDB Atlas Operations
- **Cluster Management**: Create, scale, and monitor Atlas clusters
- **Multi-Environment Setup**: Manage development, staging, production clusters
- **Access Control**: Manage database users, IP access lists
- **Monitoring**: Track cluster performance, set up alerts

## Security Features

### Read-Only Mode

Enable read-only mode to prevent write operations:

```bash
MDB_MCP_READ_ONLY=true
```

This disables all write operations (insert, update, delete) while keeping read operations available.

### Granular Tool Control

Disable specific tools or categories:

```bash
# Disable specific tools
MDB_MCP_DISABLED_TOOLS=delete,drop_collection

# Disable entire categories
MDB_MCP_DISABLED_TOOLS=atlas_tools
```

### Minimal Permissions

For production use, create MongoDB users with minimal required permissions:

```javascript
// Example: Read-only user
db.createUser({
  user: "readonly_agent",
  pwd: "secure_password",
  roles: [
    { role: "read", db: "myapp" },
    { role: "read", db: "analytics" }
  ]
})

// Example: Limited write access
db.createUser({
  user: "app_agent",
  pwd: "secure_password", 
  roles: [
    { role: "readWrite", db: "myapp" },
    { role: "read", db: "analytics" }
  ]
})
```

## Best Practices

### 1. Connection Management
- Use connection pooling for high-traffic applications
- Set appropriate connection timeouts
- Monitor connection counts and limits

### 2. Query Optimization
- Create indexes for frequently queried fields
- Use projection to limit returned fields
- Implement pagination for large result sets

```python
# Good: Use projection and limit
results = agent.mongo_find(
    database="app",
    collection="users",
    query={"status": "active"},
    projection={"name": 1, "email": 1},  # Only return needed fields
    options={"limit": 100}  # Limit results
)

# Good: Use indexes for complex queries
agent.mongo_create_index(
    database="app",
    collection="users",
    keys={"email": 1, "status": 1},  # Compound index
    options={"name": "email_status_idx"}
)
```

### 3. Error Handling
- Always handle connection errors gracefully
- Implement retry logic for transient failures
- Validate input data before database operations

### 4. Data Modeling
- Design schemas appropriate for your query patterns
- Use embedded documents for related data
- Consider sharding for very large collections

## Performance Optimization

### Indexing Strategy

```python
# Create indexes for common query patterns
agent.mongo_create_index(
    database="analytics",
    collection="events",
    keys={"user_id": 1, "event_type": 1, "timestamp": -1},
    options={"name": "user_events_idx"}
)

# Text index for search functionality
agent.mongo_create_index(
    database="content",
    collection="articles",
    keys={"title": "text", "content": "text"},
    options={"name": "article_search_idx"}
)
```

### Aggregation Optimization

```python
# Use $match early in pipeline to reduce data processed
pipeline = [
    {"$match": {"status": "active"}},  # Filter first
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]

results = agent.mongo_aggregate(
    database="app",
    collection="products",
    pipeline=pipeline
)
```

## Troubleshooting

### Common Issues

**Connection Errors**
- Verify connection string format and credentials
- Check network connectivity and firewall settings
- Ensure MongoDB server is running and accessible

**Authentication Failures**
- Verify username/password in connection string
- Check user permissions for target databases
- For Atlas: Verify API keys and project access

**Performance Issues**
- Check for missing indexes on frequently queried fields
- Monitor slow query logs
- Consider query optimization and data model changes

**Atlas API Issues**
- Verify service account has necessary permissions
- Check API key expiration and rate limits
- Ensure correct project and organization IDs

### Debug Mode

Enable debug logging:

```bash
DEBUG=mongodb-mcp* npx mongodb-mcp-server
```

## Integration with Braid

When using MongoDB MCP with Braid agents, the tools are automatically available with the `mongo_` prefix:

- `mongo_find()` - Query documents
- `mongo_insert()` - Insert documents
- `mongo_update()` - Update documents
- `mongo_delete()` - Delete documents
- `mongo_aggregate()` - Aggregation queries
- `mongo_atlas_list_clusters()` - Atlas management

The MCP runs in a separate Docker container with proper networking, data persistence, and security configurations.

## Advanced Configuration

### Custom Tool Configuration

```bash
# Disable specific tools for security
MDB_MCP_DISABLED_TOOLS=delete,drop_collection,atlas_create_cluster

# Enable read-only mode
MDB_MCP_READ_ONLY=true

# Disable telemetry
MDB_MCP_TELEMETRY_DISABLED=true
```

### Docker Networking

The MongoDB MCP supports connection to:
- Local MongoDB instances
- Remote MongoDB servers
- MongoDB Atlas clusters
- Docker-compose MongoDB services

## Support

- **MongoDB Documentation**: [https://docs.mongodb.com/](https://docs.mongodb.com/)
- **MCP Repository**: [https://github.com/mongodb-js/mongodb-mcp-server](https://github.com/mongodb-js/mongodb-mcp-server)
- **MongoDB Atlas**: [https://cloud.mongodb.com/](https://cloud.mongodb.com/)
- **Community**: MongoDB Community Forums and Discord