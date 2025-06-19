#!/usr/bin/env python3
"""
Comprehensive MCP Testing Framework
Provides automated testing for MCP servers, agents, and integrations.
"""

import os
import sys
import json
import subprocess
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TestSuite:
    """Collection of test results."""
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.status == 'passed')
    
    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.status == 'failed')
    
    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.status == 'skipped')
    
    @property
    def total_count(self) -> int:
        return len(self.results)

class MCPTestFramework:
    """Comprehensive testing framework for MCP servers and agents."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.test_suites: List[TestSuite] = []
        self.current_suite: Optional[TestSuite] = None
        
    def load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load test configuration."""
        default_config = {
            "mcp_servers": {
                "perplexity": {
                    "path": "mcp_servers/perplexity/perplexity-ask/dist/index.js",
                    "env_vars": ["PERPLEXITY_API_KEY"],
                    "required": True
                },
                "xero": {
                    "path": "mcp_servers/xero/dist/index.js",
                    "env_vars": ["XERO_ACCESS_TOKEN", "XERO_CLIENT_ID", "XERO_CLIENT_SECRET"],
                    "required": True
                },
                "notion": {
                    "path": "mcp_servers/notion/bin/cli.mjs",
                    "env_vars": ["NOTION_API_KEY"],
                    "required": True
                }
            },
            "test_timeouts": {
                "connection": 10,
                "tool_call": 30,
                "initialization": 15
            },
            "retry_config": {
                "max_retries": 3,
                "retry_delay": 2
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config file {config_file}: {e}")
        
        return default_config
    
    def start_suite(self, name: str) -> TestSuite:
        """Start a new test suite."""
        self.current_suite = TestSuite(name=name)
        self.test_suites.append(self.current_suite)
        logger.info(f"🧪 Starting test suite: {name}")
        return self.current_suite
    
    def end_suite(self):
        """End current test suite."""
        if self.current_suite:
            self.current_suite.end_time = datetime.now()
            logger.info(f"✅ Completed test suite: {self.current_suite.name} in {self.current_suite.duration:.2f}s")
    
    def add_result(self, result: TestResult):
        """Add test result to current suite."""
        if self.current_suite:
            self.current_suite.results.append(result)
            status_emoji = "✅" if result.status == "passed" else "❌" if result.status == "failed" else "⏭️"
            logger.info(f"{status_emoji} {result.name}: {result.status} ({result.duration:.2f}s)")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run an individual test with timing and error handling."""
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, tuple):
                success, message, details = result
            elif isinstance(result, bool):
                success, message, details = result, "", {}
            else:
                success, message, details = True, str(result), {}
            
            status = "passed" if success else "failed"
            
            return TestResult(
                name=test_name,
                status=status,
                duration=duration,
                message=message,
                details=details
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                status="failed",
                duration=duration,
                message=str(e),
                details={"exception": type(e).__name__}
            )
    
    def test_mcp_server_connection(self, server_name: str, server_config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Test connection to a single MCP server."""
        # Check environment variables
        missing_vars = []
        env_vars = {}
        
        for var in server_config.get("env_vars", []):
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                env_vars[var] = value
        
        if missing_vars:
            return False, f"Missing environment variables: {', '.join(missing_vars)}", {}
        
        # Start server process
        server_path = server_config["path"]
        if not os.path.exists(server_path):
            return False, f"Server path not found: {server_path}", {}
        
        try:
            env = os.environ.copy()
            env.update(env_vars)
            
            process = subprocess.Popen(
                ['node', server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "mcp-test-framework",
                        "version": "1.0.0"
                    }
                }
            }
            
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response with timeout
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    # Get tools list
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    process.stdin.write(json.dumps(tools_request) + "\n")
                    process.stdin.flush()
                    
                    tools_response_line = process.stdout.readline()
                    tools_count = 0
                    if tools_response_line:
                        tools_response = json.loads(tools_response_line)
                        if "result" in tools_response:
                            tools_count = len(tools_response["result"].get("tools", []))
                    
                    process.terminate()
                    return True, f"Connected successfully, {tools_count} tools available", {
                        "tools_count": tools_count,
                        "server_response": response.get("result", {})
                    }
                else:
                    process.terminate()
                    return False, f"Initialization failed: {response}", {}
            else:
                process.terminate()
                return False, "No response received", {}
                
        except Exception as e:
            return False, f"Connection error: {e}", {}
    
    def test_mcp_tool_call(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Test calling a specific tool on an MCP server."""
        server_config = self.config["mcp_servers"].get(server_name)
        if not server_config:
            return False, f"Unknown server: {server_name}", {}
        
        # Start server (reuse connection logic)
        connection_success, connection_message, connection_details = self.test_mcp_server_connection(server_name, server_config)
        if not connection_success:
            return False, f"Could not connect to server: {connection_message}", {}
        
        try:
            # Start server process again for tool call
            env = os.environ.copy()
            for var in server_config.get("env_vars", []):
                if os.getenv(var):
                    env[var] = os.getenv(var)
            
            process = subprocess.Popen(
                ['node', server_config["path"]],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-test-framework", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            process.stdout.readline()  # Read init response
            
            # Call tool
            tool_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            process.stdin.write(json.dumps(tool_request) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    process.terminate()
                    return True, "Tool call successful", {"result": response["result"]}
                else:
                    process.terminate()
                    return False, f"Tool call failed: {response}", {}
            else:
                process.terminate()
                return False, "No response to tool call", {}
                
        except Exception as e:
            return False, f"Tool call error: {e}", {}
    
    def test_agent_integration(self, agent_class, test_queries: List[str]) -> Tuple[bool, str, Dict[str, Any]]:
        """Test agent integration with MCP servers."""
        try:
            # Import agent class dynamically
            if isinstance(agent_class, str):
                module_name, class_name = agent_class.rsplit('.', 1)
                module = __import__(module_name, fromlist=[class_name])
                agent_class = getattr(module, class_name)
            
            # Create agent instance
            agent = agent_class()
            
            # Test startup
            if not agent.startup():
                return False, "Agent startup failed", {}
            
            results = []
            for query in test_queries:
                try:
                    response = agent.run(query)
                    if response and len(response) > 0:
                        results.append({"query": query, "success": True, "response_length": len(response)})
                    else:
                        results.append({"query": query, "success": False, "error": "Empty response"})
                except Exception as e:
                    results.append({"query": query, "success": False, "error": str(e)})
            
            # Cleanup
            agent.shutdown()
            
            successful_queries = sum(1 for r in results if r["success"])
            total_queries = len(results)
            
            return True, f"Agent integration test completed: {successful_queries}/{total_queries} queries successful", {
                "results": results,
                "success_rate": successful_queries / total_queries if total_queries > 0 else 0
            }
            
        except Exception as e:
            return False, f"Agent integration test failed: {e}", {}
    
    def run_performance_tests(self, iterations: int = 10) -> Tuple[bool, str, Dict[str, Any]]:
        """Run performance tests on MCP servers."""
        performance_data = {}
        
        for server_name, server_config in self.config["mcp_servers"].items():
            if not all(os.getenv(var) for var in server_config.get("env_vars", [])):
                continue
            
            connection_times = []
            
            for i in range(iterations):
                start_time = time.time()
                success, _, _ = self.test_mcp_server_connection(server_name, server_config)
                duration = time.time() - start_time
                
                if success:
                    connection_times.append(duration)
            
            if connection_times:
                performance_data[server_name] = {
                    "mean_connection_time": sum(connection_times) / len(connection_times),
                    "min_connection_time": min(connection_times),
                    "max_connection_time": max(connection_times),
                    "success_rate": len(connection_times) / iterations
                }
        
        return True, f"Performance tests completed for {len(performance_data)} servers", performance_data
    
    def run_full_test_suite(self, include_performance: bool = False, agent_class: Optional[str] = None) -> List[TestSuite]:
        """Run the complete test suite."""
        # Environment tests
        env_suite = self.start_suite("Environment Tests")
        
        # Test environment variables
        result = self.run_test("Environment Variables", self.test_environment_variables)
        self.add_result(result)
        
        self.end_suite()
        
        # MCP Connection tests
        conn_suite = self.start_suite("MCP Connection Tests")
        
        for server_name, server_config in self.config["mcp_servers"].items():
            result = self.run_test(f"{server_name.title()} MCP Connection", 
                                 self.test_mcp_server_connection, server_name, server_config)
            self.add_result(result)
        
        self.end_suite()
        
        # Tool tests
        tool_suite = self.start_suite("MCP Tool Tests")
        
        # Test basic tool calls
        tool_tests = [
            ("perplexity", "perplexity_ask", {"messages": [{"role": "user", "content": "Hello"}]}),
            ("xero", "list-xero-organisations", {}),
            ("notion", "API-get-users", {})
        ]
        
        for server_name, tool_name, arguments in tool_tests:
            if server_name in self.config["mcp_servers"]:
                result = self.run_test(f"{server_name.title()} {tool_name}", 
                                     self.test_mcp_tool_call, server_name, tool_name, arguments)
                self.add_result(result)
        
        self.end_suite()
        
        # Agent integration tests
        if agent_class:
            agent_suite = self.start_suite("Agent Integration Tests")
            
            test_queries = [
                "Hello, how are you?",
                "What's the weather like?",
                "Give me a brief summary of something interesting"
            ]
            
            result = self.run_test("Agent Integration", self.test_agent_integration, agent_class, test_queries)
            self.add_result(result)
            
            self.end_suite()
        
        # Performance tests
        if include_performance:
            perf_suite = self.start_suite("Performance Tests")
            
            result = self.run_test("Connection Performance", self.run_performance_tests, 5)
            self.add_result(result)
            
            self.end_suite()
        
        return self.test_suites
    
    def test_environment_variables(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Test environment variable setup."""
        missing_vars = []
        present_vars = []
        
        all_vars = set()
        for server_config in self.config["mcp_servers"].values():
            all_vars.update(server_config.get("env_vars", []))
        
        for var in all_vars:
            if os.getenv(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)
        
        # Check for core variables
        core_vars = ["OPENAI_API_KEY"]
        missing_core = [var for var in core_vars if not os.getenv(var)]
        
        if missing_core:
            return False, f"Missing core environment variables: {', '.join(missing_core)}", {
                "missing_core": missing_core,
                "missing_mcp": missing_vars,
                "present": present_vars
            }
        
        return True, f"Environment check passed: {len(present_vars)} vars present, {len(missing_vars)} missing", {
            "missing_mcp": missing_vars,
            "present": present_vars
        }
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate test report."""
        report_lines = []
        report_lines.append("# MCP Test Framework Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")
        
        total_passed = sum(suite.passed_count for suite in self.test_suites)
        total_failed = sum(suite.failed_count for suite in self.test_suites)
        total_skipped = sum(suite.skipped_count for suite in self.test_suites)
        total_tests = sum(suite.total_count for suite in self.test_suites)
        
        report_lines.append("## Summary")
        report_lines.append(f"- Total Tests: {total_tests}")
        report_lines.append(f"- Passed: {total_passed}")
        report_lines.append(f"- Failed: {total_failed}")
        report_lines.append(f"- Skipped: {total_skipped}")
        report_lines.append(f"- Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "- Success Rate: N/A")
        report_lines.append("")
        
        for suite in self.test_suites:
            report_lines.append(f"## {suite.name}")
            report_lines.append(f"Duration: {suite.duration:.2f}s")
            report_lines.append(f"Results: {suite.passed_count} passed, {suite.failed_count} failed, {suite.skipped_count} skipped")
            report_lines.append("")
            
            for result in suite.results:
                status_emoji = "✅" if result.status == "passed" else "❌" if result.status == "failed" else "⏭️"
                report_lines.append(f"### {status_emoji} {result.name}")
                report_lines.append(f"- Status: {result.status}")
                report_lines.append(f"- Duration: {result.duration:.2f}s")
                if result.message:
                    report_lines.append(f"- Message: {result.message}")
                if result.details:
                    report_lines.append(f"- Details: {json.dumps(result.details, indent=2)}")
                report_lines.append("")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_file}")
        
        return report

def main():
    """Main CLI interface for the test framework."""
    parser = argparse.ArgumentParser(description='MCP Test Framework')
    parser.add_argument('--config', help='Test configuration file')
    parser.add_argument('--output', help='Output report file')
    parser.add_argument('--performance', action='store_true', help='Include performance tests')
    parser.add_argument('--agent', help='Agent class to test (module.ClassName)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, skipping .env file loading")
    
    # Create framework
    framework = MCPTestFramework(args.config)
    
    # Run tests
    print("🚀 Starting MCP Test Framework")
    print("=" * 60)
    
    suites = framework.run_full_test_suite(
        include_performance=args.performance,
        agent_class=args.agent
    )
    
    # Generate report
    report = framework.generate_report(args.output)
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    total_passed = sum(suite.passed_count for suite in suites)
    total_failed = sum(suite.failed_count for suite in suites)
    total_tests = sum(suite.total_count for suite in suites)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "Success Rate: N/A")
    
    if total_failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())