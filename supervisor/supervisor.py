"""
Supervisor Agent
Manages and coordinates multiple child agents in the LangGraph system.
"""
import os
import sys
import json
from typing import Dict, Any, List, Callable, Optional, TypedDict, Union
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.power_analysis_agent import create_power_analysis_agent


# Define agent types
class AgentType(str, Enum):
    POWER_ANALYSIS = "power_analysis"
    # Future agent types will be added here


# Define the supervisor state
class SupervisorState(TypedDict):
    """State for the Supervisor Agent."""
    query: str
    agent_type: Optional[str]
    agent_args: Dict[str, Any]
    result: Optional[str]


# Define the routing system prompt
ROUTING_PROMPT = """You are a supervisor agent responsible for routing user queries to the appropriate specialized agents.
Currently, the system supports these agent types:

1. Power Analysis Agent - Compares two weeks of power usage data and provides a comprehensive analysis.

Analyze the user query and determine which agent should handle it. If the query requires power analysis, 
extract the paths to the two JSON files that need to be compared.

User Query: {query}

Return a JSON object with:
1. "agent_type": The type of agent to use (use "power_analysis" for the Power Analysis Agent)
2. "agent_args": A dictionary of arguments needed by the agent (for Power Analysis, this should include "week1_path" and "week2_path")

Example response:
```json
{
  "agent_type": "power_analysis",
  "agent_args": {
    "week1_path": "/path/to/week1.json",
    "week2_path": "/path/to/week2.json"
  }
}
```

If the query doesn't match any supported agent functionality, respond with:
```json
{
  "agent_type": null,
  "agent_args": {}
}
```
"""


def create_supervisor():
    """
    Creates a supervisor agent that routes tasks to appropriate child agents.
    
    Returns:
        A callable function that handles incoming queries
    """
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    
    # Create the routing prompt template
    routing_prompt = ChatPromptTemplate.from_template(ROUTING_PROMPT)
    
    # Create child agents
    power_analysis_agent = create_power_analysis_agent()
    
    # Define the nodes for the graph
    def route_query(state: SupervisorState) -> SupervisorState:
        """Route the query to the appropriate agent."""
        query = state["query"]
        
        # Use the LLM to route the query
        routing_chain = routing_prompt | llm
        response = routing_chain.invoke({"query": query})
        
        # Extract the routing information from the response
        response_text = response.content
        
        # Extract the JSON from the response (handling potential markdown codeblocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text.strip()
        
        routing_info = json.loads(json_str)
        
        return {
            "query": query,
            "agent_type": routing_info.get("agent_type"),
            "agent_args": routing_info.get("agent_args", {}),
            "result": None
        }
    
    def call_power_analysis(state: SupervisorState) -> SupervisorState:
        """Call the power analysis agent."""
        week1_path = state["agent_args"].get("week1_path")
        week2_path = state["agent_args"].get("week2_path")
        
        # Validate paths
        if not week1_path or not week2_path:
            result = "Error: Missing required file paths for power analysis."
        elif not os.path.exists(week1_path) or not os.path.exists(week2_path):
            result = "Error: One or both specified files do not exist."
        else:
            # Call the power analysis agent
            result = power_analysis_agent(week1_path, week2_path)
        
        return {
            "query": state["query"],
            "agent_type": state["agent_type"],
            "agent_args": state["agent_args"],
            "result": result
        }
    
    def handle_unsupported(state: SupervisorState) -> SupervisorState:
        """Handle unsupported queries."""
        return {
            "query": state["query"],
            "agent_type": state["agent_type"],
            "agent_args": state["agent_args"],
            "result": "Sorry, I don't have an agent that can handle this request. Currently, I support power analysis tasks."
        }
    
    # Define edges for conditional routing
    def route_edges(state: SupervisorState) -> str:
        """Determine which agent to route to based on the agent_type."""
        agent_type = state["agent_type"]
        
        if agent_type == AgentType.POWER_ANALYSIS:
            return "power_analysis"
        else:
            return "unsupported"
    
    # Create the graph
    workflow = StateGraph(SupervisorState)
    
    # Add nodes
    workflow.add_node("router", route_query)
    workflow.add_node("power_analysis", call_power_analysis)
    workflow.add_node("unsupported", handle_unsupported)
    
    # Add edges
    workflow.add_edge("router", route_edges)
    workflow.add_conditional_edges(
        "router",
        route_edges,
        {
            "power_analysis": "power_analysis",
            "unsupported": "unsupported"
        }
    )
    workflow.add_edge("power_analysis", END)
    workflow.add_edge("unsupported", END)
    
    # Set the entrypoint
    workflow.set_entry_point("router")
    
    # Compile the graph
    graph = workflow.compile()
    
    def supervisor_agent(query: str) -> str:
        """
        Process a user query through the supervisor system.
        
        Args:
            query: The user's query
            
        Returns:
            The response from the appropriate agent, or an error message
        """
        # Initialize the state
        initial_state = SupervisorState(
            query=query,
            agent_type=None,
            agent_args={},
            result=None
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        return final_state["result"]
    
    return supervisor_agent


def cli():
    """Command line interface for the supervisor agent."""
    if len(sys.argv) < 2:
        print("Usage: python supervisor.py <query>")
        print("Example: python supervisor.py 'Analyze power data from data/example_week1.json and data/example_week2.json'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    supervisor = create_supervisor()
    result = supervisor(query)
    
    print("\n" + "=" * 80)
    print("SUPERVISOR RESPONSE")
    print("=" * 80 + "\n")
    print(result)


if __name__ == "__main__":
    cli()