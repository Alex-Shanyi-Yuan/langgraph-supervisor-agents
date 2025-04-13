"""
Power Analysis Agent
Takes in two JSON files (week1, week2) and summarizes power usage differences.
"""
from typing import Dict, Any, List, Tuple, Optional, Annotated, TypedDict
import json
import os
from pathlib import Path
import sys

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.parser import load_power_data, compare_weeks


# Define the state for the power analysis agent
class PowerAnalysisState(TypedDict):
    """State for the Power Analysis Agent."""
    week1_data: Dict[str, Any]
    week2_data: Dict[str, Any]
    comparison: Optional[Dict[str, Any]]
    summary: Optional[str]


# Define the system prompt for the power analysis LLM
POWER_ANALYSIS_PROMPT = """You are an expert energy analyst specialized in analyzing power usage data.
Your task is to analyze the power usage data from two different weeks and provide a thorough analysis.

Here is the comparison data between the two weeks:
{comparison_data}

Provide a comprehensive analysis that includes:
1. Overall trends in total power usage
2. Device-specific usage changes
3. Weekday vs weekend patterns
4. Peak usage time patterns
5. Noteworthy anomalies or changes
6. Potential optimization recommendations based on the observed patterns

Your analysis should be data-driven, highlighting percentages and specific numbers where relevant.
Format your response in a clear, professional manner with appropriate sections and bullet points when listing multiple items.
"""


def create_power_analysis_agent(model_name: str = "gpt-4o"):
    """
    Creates a power analysis agent using LangGraph.
    
    Args:
        model_name: The name of the OpenAI model to use
        
    Returns:
        A callable function that analyzes two weeks of power data
    """
    llm = ChatOpenAI(model_name=model_name, temperature=0.1)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_template(POWER_ANALYSIS_PROMPT)
    
    # Define the nodes for the graph
    def load_data(state: PowerAnalysisState) -> PowerAnalysisState:
        """Load and validate the input data."""
        return state
    
    def analyze_data(state: PowerAnalysisState) -> PowerAnalysisState:
        """Compare the two weeks of data."""
        comparison = compare_weeks(state["week1_data"], state["week2_data"])
        return {"week1_data": state["week1_data"], 
                "week2_data": state["week2_data"], 
                "comparison": comparison,
                "summary": None}
    
    def generate_summary(state: PowerAnalysisState) -> PowerAnalysisState:
        """Generate a summary using the LLM."""
        comparison_data = json.dumps(state["comparison"], indent=2)
        
        chain = prompt | llm | StrOutputParser()
        summary = chain.invoke({"comparison_data": comparison_data})
        
        return {"week1_data": state["week1_data"], 
                "week2_data": state["week2_data"], 
                "comparison": state["comparison"],
                "summary": summary}
    
    # Create the graph
    workflow = StateGraph(PowerAnalysisState)
    
    # Add nodes
    workflow.add_node("load_data", load_data)
    workflow.add_node("analyze_data", analyze_data)
    workflow.add_node("generate_summary", generate_summary)
    
    # Add edges
    workflow.add_edge("load_data", "analyze_data")
    workflow.add_edge("analyze_data", "generate_summary")
    workflow.add_edge("generate_summary", END)
    
    # Set the entrypoint
    workflow.set_entry_point("load_data")
    
    # Compile the graph
    graph = workflow.compile()
    
    def power_analysis_agent(week1_path: str, week2_path: str) -> str:
        """
        Analyze two weeks of power data.
        
        Args:
            week1_path: Path to the first week's data
            week2_path: Path to the second week's data
            
        Returns:
            A summary analysis of the two weeks
        """
        # Load the data
        week1_data = load_power_data(week1_path)
        week2_data = load_power_data(week2_path)
        
        # Initialize the state
        initial_state = PowerAnalysisState(
            week1_data=week1_data,
            week2_data=week2_data,
            comparison=None,
            summary=None
        )
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        return final_state["summary"]
    
    return power_analysis_agent


def cli():
    """Command line interface for the power analysis agent."""
    if len(sys.argv) != 3:
        print("Usage: python power_analysis_agent.py <week1_file> <week2_file>")
        sys.exit(1)
    
    week1_path = sys.argv[1]
    week2_path = sys.argv[2]
    
    if not os.path.exists(week1_path) or not os.path.exists(week2_path):
        print(f"Error: One or both files do not exist.")
        sys.exit(1)
    
    agent = create_power_analysis_agent()
    summary = agent(week1_path, week2_path)
    
    print("\n" + "=" * 80)
    print("POWER ANALYSIS SUMMARY")
    print("=" * 80 + "\n")
    print(summary)


if __name__ == "__main__":
    cli()