# Braid Agent Builder: Project Roadmap

This document outlines the future development direction for the Braid - Agent Builder. Our goal is to create a robust framework for developing, testing, and deploying enterprise-grade AI agents.

## Phase 1: Core Tool Test Agents
The immediate priority is to ensure the reliability of our core tool integrations. We will build dedicated agents to test the full functionality of these essential services.

- [ ] **Microsoft 365 Test Agent:** Develop an agent to test and validate all core Microsoft 365 tools, including Teams message posting and Outlook email functionality.
- [ ] **Slack Test Agent:** Develop an agent to test and validate core Slack integration tools, such as posting messages and uploading files.
- [ ] **Build Additional Test Agents:** Create a suite of test agents to validate other key integrations and common use cases with eventually vertical and industry specific tool libraries.

## Phase 2: Autonomous Evaluation Module
To ensure agents are reliable before they are deployed, we will build a sophisticated evaluation module.

- [ ] **Develop Evaluation Module:** This module will be designed to autonomously test agents against a range of scenarios, including common failure points and critical edge cases. It will programmatically analyze agent performance to ensure it meets objectives before deployment.

1. Running pre defined prompt sets to evaluate responses and provide a list of recommended improvements across agent prompting/instruction in the sequences by diagnosing verbose mode response and where the agent performance may be degrating 
2. Think through the evaluation metrics specific to this agent and where common fault points or errors may be (E.g. Hallucinations, API failues (if applicable) ect. 
3. Analyze and rate the overall response on the basis of quality, consistency, reliability, and meeting th euser's objective. Test a combination for core cases and hypothetical common edge cases. 
4. Provide a file of 'evaluation' with an analysis of these metrics after your run to test the results and then lastly give recommended suggested changes in a new file 'EvaluationSuggestions' to give feedback to our team for suggested improvements 

## Phase 3: Deployment Module
The final step is to streamline the path to production.

- [ ] **LangGraph Deployment Module:** Build a dedicated module to prepare and package agents for seamless deployment to LangGraph. This will handle dependency management, configuration, and final validation, making the transition from development to production as smooth as possible.