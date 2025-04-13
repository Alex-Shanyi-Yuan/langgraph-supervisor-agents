# LangGraph Multi-Agent System

A modular multi-agent system built with LangGraph, featuring a Supervisor Architecture pattern that manages and coordinates multiple specialized child agents.

## 🧠 Overview

This project demonstrates a multi-agent system architecture where a central Supervisor Agent routes user requests to specialized child agents. The system is designed with extensibility in mind, making it easy to add new agent types in the future.

Currently, the system includes:

- **Supervisor Agent**: Routes user queries to appropriate specialized agents
- **Power Analysis Agent**: Analyzes and compares two weeks of power usage data

### Components

1. **Supervisor Agent**:
   - Central control node that routes user requests
   - Manages all child agents in the system
   - Handles input parsing and output formatting
   - Easily extensible to add more agent types

2. **Power Analysis Agent**:
   - Specialized agent for power usage data analysis
   - Takes two JSON datasets representing weekly power usage
   - Provides detailed analysis and comparisons
   - Can identify trends, anomalies, and optimization opportunities

### Technical Implementation

The system is built using:
- **LangGraph**: For creating the agent workflow graphs
- **LangChain**: For building the LLM chains
- **OpenAI**: For the underlying LLM models

Each agent is implemented as a directed graph with specialized nodes for different processing steps.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.13.2 or later
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/langgraph-supervisor-agents.git
   cd langgraph-supervisor-agents
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 🚀 Usage

The system can be used in two ways:

### Via the Supervisor (recommended)

For natural language queries that will be routed to the appropriate agent:

```bash
python main.py supervisor "Analyze the power usage data from data/example_week1.json and data/example_week2.json"
```

### Direct Agent Access

For directly accessing a specific agent:

```bash
python main.py power --week1 data/example_week1.json --week2 data/example_week2.json
```

### CLI for Individual Agents

Each agent also has its own CLI interface:

```bash
# Power Analysis Agent
python agents/power_analysis_agent.py data/example_week1.json data/example_week2.json

# Supervisor Agent
python supervisor/supervisor.py "Analyze the power usage data from data/example_week1.json and data/example_week2.json"
```

## 🧪 Testing

Run the tests with:

```bash
python -m unittest discover -s tests
```

## 📝 Adding New Agents

The system is designed to be easily extensible. To add a new agent:

1. Create a new agent module in the `agents/` directory
2. Implement the agent using the LangGraph StateGraph pattern
3. Update the Supervisor Agent to recognize and route to the new agent:
   - Add the new agent type to the `AgentType` enum
   - Create an instance of your agent in the supervisor
   - Add a new handler function for your agent
   - Update the routing logic in the supervisor

## 🔮 Future Work

Potential future enhancements include:

1. **New Agent Types**:
   - Text Analysis Agent: For analyzing document collections
   - Forecast Agent: For predicting future power usage based on historical data
   - Anomaly Detection Agent: For identifying unusual patterns in power consumption
   - Recommendation Agent: For suggesting energy conservation measures

2. **Enhanced Supervisor Capabilities**:
   - Multi-step reasoning for complex queries
   - Memory of past interactions
   - Ability to orchestrate multiple agents for a single task

3. **System Improvements**:
   - Web interface for easier interaction
   - Persistent storage for analysis results
   - Integration with real-time data sources
   - Support for visualization of analysis results

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.