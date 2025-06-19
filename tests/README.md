# MCP Testing Framework

Comprehensive testing framework for MCP (Model Context Protocol) servers and agents.

## Overview

The MCP Testing Framework provides automated testing capabilities for:
- MCP server connections and initialization
- Tool functionality and performance
- Agent integration with MCP servers
- End-to-end workflow validation
- Performance benchmarking

## Quick Start

### Basic Testing

```bash
# Test all MCP connections
python tests/mcp_test_framework.py

# Test with custom configuration
python tests/mcp_test_framework.py --config tests/test_config.json

# Include performance tests
python tests/mcp_test_framework.py --performance

# Generate detailed report
python tests/mcp_test_framework.py --output test_report.md
```

### Agent Testing

```bash
# Test agent integration
python tests/mcp_test_framework.py --agent templates.mcp-agent.agent.MCPAgent

# Full test suite with agent
python tests/mcp_test_framework.py --agent templates.mcp-agent.agent.MCPAgent --performance --output full_report.md
```

## Test Suites

### 1. Environment Tests
- Validates required environment variables
- Checks API key configuration
- Verifies system dependencies

### 2. MCP Connection Tests
- Tests connection to each MCP server
- Validates initialization protocol
- Checks server responsiveness

### 3. Tool Functionality Tests
- Tests individual MCP tools
- Validates tool parameters and responses
- Checks error handling

### 4. Agent Integration Tests
- Tests agent startup and shutdown
- Validates MCP tool integration
- Tests end-to-end workflows

### 5. Performance Tests (Optional)
- Measures connection times
- Tests concurrent connections
- Benchmarks tool response times

## Configuration

### Test Configuration File

Create a `test_config.json` file to customize testing:

```json
{
  "mcp_servers": {
    "perplexity": {
      "path": "mcp_servers/perplexity/perplexity-ask/dist/index.js",
      "env_vars": ["PERPLEXITY_API_KEY"],
      "required": true,
      "test_tools": ["perplexity_ask", "perplexity_research"]
    }
  },
  "test_timeouts": {
    "connection": 15,
    "tool_call": 45,
    "initialization": 20
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

### Environment Variables

Required for testing:

```bash
# Core
OPENAI_API_KEY=your_openai_key

# MCP Servers (as needed)
PERPLEXITY_API_KEY=your_perplexity_key
XERO_ACCESS_TOKEN=your_xero_token
NOTION_API_KEY=your_notion_key
```

## Usage Examples

### Programmatic Usage

```python
from tests.mcp_test_framework import MCPTestFramework

# Create framework
framework = MCPTestFramework('tests/test_config.json')

# Run specific test suite
suite = framework.start_suite("Custom Tests")

# Run individual test
result = framework.run_test("Test Name", test_function, *args)
framework.add_result(result)

framework.end_suite()

# Generate report
report = framework.generate_report('my_report.md')
```

### Custom Test Functions

```python
def custom_mcp_test(server_name: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Custom test function."""
    try:
        # Your test logic here
        success = True
        message = "Test passed"
        details = {"custom_data": "value"}
        
        return success, message, details
    except Exception as e:
        return False, str(e), {}

# Use in framework
result = framework.run_test("Custom Test", custom_mcp_test, "perplexity")
```

## Test Reports

### Report Format

Reports are generated in Markdown format with:
- Executive summary with pass/fail counts
- Detailed results for each test suite
- Performance metrics (if included)
- Error details and debugging information

### Sample Report Structure

```markdown
# MCP Test Framework Report
Generated: 2024-01-15T10:30:00

## Summary
- Total Tests: 15
- Passed: 12
- Failed: 2  
- Skipped: 1
- Success Rate: 80.0%

## Environment Tests
Duration: 1.23s
Results: 2 passed, 0 failed, 0 skipped

### ✅ Environment Variables
- Status: passed
- Duration: 0.15s
- Message: Environment check passed: 5 vars present, 2 missing
```

## CI/CD Integration

### GitHub Actions

```yaml
name: MCP Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        ./scripts/setup_mcp_servers.sh --no-test
        
    - name: Run MCP tests
      env:
        PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
        XERO_ACCESS_TOKEN: ${{ secrets.XERO_ACCESS_TOKEN }}
        NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
      run: |
        python tests/mcp_test_framework.py --output test_report.md
        
    - name: Upload test report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: test_report.md
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        PERPLEXITY_API_KEY = credentials('perplexity-api-key')
        XERO_ACCESS_TOKEN = credentials('xero-access-token')
        NOTION_API_KEY = credentials('notion-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh './scripts/setup_mcp_servers.sh --no-test'
            }
        }
        
        stage('Test') {
            steps {
                sh 'python tests/mcp_test_framework.py --performance --output test_report.md'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test_report.md'
                }
            }
        }
    }
}
```

## Advanced Features

### Custom Test Suites

```python
class CustomMCPTests(MCPTestFramework):
    def test_custom_workflow(self):
        """Test custom business logic."""
        suite = self.start_suite("Custom Workflow Tests")
        
        # Test 1: Data flow
        result = self.run_test("Data Flow", self.test_data_flow)
        self.add_result(result)
        
        # Test 2: Error handling
        result = self.run_test("Error Handling", self.test_error_handling)
        self.add_result(result)
        
        self.end_suite()
        return suite
```

### Performance Monitoring

```python
# Monitor performance over time
framework = MCPTestFramework()
suite = framework.start_suite("Performance Monitoring")

for i in range(10):
    result = framework.run_test(f"Iteration {i+1}", 
                               framework.test_mcp_server_connection, 
                               "perplexity", config)
    framework.add_result(result)

framework.end_suite()
```

### Load Testing

```python
import concurrent.futures

def load_test_mcp_servers(concurrent_connections: int = 5):
    """Run load tests with multiple concurrent connections."""
    framework = MCPTestFramework()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_connections) as executor:
        futures = []
        
        for i in range(concurrent_connections):
            future = executor.submit(framework.test_mcp_server_connection, 
                                   "perplexity", config)
            futures.append(future)
        
        results = [future.result() for future in futures]
        
    return results
```

## Troubleshooting

### Common Issues

1. **Server Connection Failures**
   ```bash
   # Check if MCP servers are properly installed
   ./scripts/setup_mcp_servers.sh
   
   # Verify environment variables
   python tests/mcp_test_framework.py --verbose
   ```

2. **Tool Call Timeouts**
   ```json
   // Increase timeouts in test_config.json
   {
     "test_timeouts": {
       "tool_call": 60
     }
   }
   ```

3. **Agent Integration Issues**
   ```bash
   # Test agent independently first
   python templates/mcp-agent/test_agent.py --test-workflow
   ```

### Debug Mode

```bash
# Enable verbose logging
python tests/mcp_test_framework.py --verbose

# Check individual components
python -c "
from tests.mcp_test_framework import MCPTestFramework
fw = MCPTestFramework()
result = fw.test_environment_variables()
print(result)
"
```

## Best Practices

1. **Test Organization**
   - Group related tests into suites
   - Use descriptive test names
   - Include setup and teardown logic

2. **Environment Management**
   - Use separate test environments
   - Mock external dependencies when possible
   - Validate environment before testing

3. **Error Handling**
   - Capture detailed error information
   - Implement retry logic for flaky tests
   - Provide clear failure messages

4. **Performance Testing**
   - Establish baseline metrics
   - Monitor performance trends
   - Test under realistic load conditions

5. **Reporting**
   - Generate reports for every test run
   - Include relevant debugging information
   - Track test results over time

## Next Steps

- Integrate with monitoring systems
- Add more sophisticated load testing
- Implement test data management
- Create visual test dashboards
- Add automated test scheduling

For more information, see:
- [MCP Setup Guide](../docs/guides/mcp-integration/MCP_SETUP_GUIDE.md)
- [MCP Deployment Guide](../docs/guides/mcp-integration/MCP_DEPLOYMENT_GUIDE.md)