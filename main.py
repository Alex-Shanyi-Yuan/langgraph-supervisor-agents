"""
LangGraph Multi-Agent System for Power Analysis
Main entry point for the application.
"""
import os
import sys
import argparse
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

from supervisor.supervisor import create_supervisor
from agents.power_analysis_agent import create_power_analysis_agent


def main():
    """Main entry point for the LangGraph multi-agent system."""
    console = Console()
    
    parser = argparse.ArgumentParser(
        description="LangGraph Multi-Agent System with Supervisor Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Supervisor command
    supervisor_parser = subparsers.add_parser("supervisor", help="Use the supervisor agent to route queries")
    supervisor_parser.add_argument("query", nargs="+", help="The query to process")
    
    # Power analysis command
    power_parser = subparsers.add_parser("power", help="Directly use the power analysis agent")
    power_parser.add_argument("--week1", required=True, help="Path to the first week's data JSON file")
    power_parser.add_argument("--week2", required=True, help="Path to the second week's data JSON file")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        console.print(Panel(
            "[bold cyan]LangGraph Multi-Agent System[/bold cyan]\n\n"
            "A modular multi-agent system using LangGraph with a Supervisor Architecture pattern.\n\n"
            "Use [bold]--help[/bold] for more information.",
            title="Welcome"
        ))
        parser.print_help()
        return
    
    # Process based on command
    if args.command == "supervisor":
        query = " ".join(args.query)
        console.print(Panel(f"Processing query: [bold]{query}[/bold]", title="Supervisor Agent"))
        
        supervisor_agent = create_supervisor()
        result = supervisor_agent(query)
        
        console.print(Panel(result, title="Supervisor Response"))
        
    elif args.command == "power":
        week1_path = args.week1
        week2_path = args.week2
        
        # Validate file paths
        if not os.path.exists(week1_path):
            console.print(f"[bold red]Error:[/bold red] Week 1 file not found: {week1_path}")
            return
            
        if not os.path.exists(week2_path):
            console.print(f"[bold red]Error:[/bold red] Week 2 file not found: {week2_path}")
            return
        
        console.print(Panel(
            f"Analyzing power usage data:\n"
            f"[bold]Week 1:[/bold] {week1_path}\n"
            f"[bold]Week 2:[/bold] {week2_path}",
            title="Power Analysis Agent"
        ))
        
        power_agent = create_power_analysis_agent()
        result = power_agent(week1_path, week2_path)
        
        console.print(Panel(result, title="Power Analysis Results"))


if __name__ == "__main__":
    main()