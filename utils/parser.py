"""
Parser utility for handling power usage data files.
"""
import json
from typing import Dict, Any, List, Tuple
import os
from pathlib import Path


def load_power_data(file_path: str) -> Dict[str, Any]:
    """
    Load power usage data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the power usage data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def get_week_total_usage(data: Dict[str, Any]) -> float:
    """
    Calculate the total power usage for the week.
    
    Args:
        data: Power usage data dictionary
        
    Returns:
        Total kWh usage for the week
    """
    return sum(day["total_kwh"] for day in data["daily_usage"])


def get_device_usage_breakdown(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate the total usage by device type for the week.
    
    Args:
        data: Power usage data dictionary
        
    Returns:
        Dictionary with device types as keys and total kWh as values
    """
    device_totals = {}
    
    for day in data["daily_usage"]:
        for device, usage in day["devices"].items():
            if device not in device_totals:
                device_totals[device] = 0
            device_totals[device] += usage
    
    return device_totals


def calculate_daily_averages(data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate daily average power usage.
    
    Args:
        data: Power usage data dictionary
        
    Returns:
        Dictionary with average usage statistics
    """
    num_days = len(data["daily_usage"])
    
    return {
        "avg_daily_kwh": sum(day["total_kwh"] for day in data["daily_usage"]) / num_days,
        "avg_peak_value": sum(day["peak_value"] for day in data["daily_usage"]) / num_days
    }


def find_usage_patterns(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify patterns in the power usage data.
    
    Args:
        data: Power usage data dictionary
        
    Returns:
        Dictionary with pattern information
    """
    weekday_usage = []
    weekend_usage = []
    
    for day in data["daily_usage"]:
        # Basic weekend detection (this is simplified)
        date_parts = day["date"].split("-")
        day_index = int(date_parts[2])
        
        # Assuming the data starts on a weekday and follows a 7-day week pattern
        if day_index % 7 == 3 or day_index % 7 == 4:  # Simple weekend detection
            weekend_usage.append(day["total_kwh"])
        else:
            weekday_usage.append(day["total_kwh"])
    
    return {
        "weekday_avg": sum(weekday_usage) / len(weekday_usage) if weekday_usage else 0,
        "weekend_avg": sum(weekend_usage) / len(weekend_usage) if weekend_usage else 0,
        "weekday_vs_weekend_diff_pct": 
            ((sum(weekday_usage) / len(weekday_usage) if weekday_usage else 0) - 
             (sum(weekend_usage) / len(weekend_usage) if weekend_usage else 0)) / 
            (sum(weekday_usage) / len(weekday_usage) if weekday_usage else 1) * 100
    }


def compare_weeks(week1_data: Dict[str, Any], week2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two weeks of power usage data.
    
    Args:
        week1_data: First week's power usage data
        week2_data: Second week's power usage data
        
    Returns:
        Dictionary with comparison metrics
    """
    week1_total = get_week_total_usage(week1_data)
    week2_total = get_week_total_usage(week2_data)
    
    week1_devices = get_device_usage_breakdown(week1_data)
    week2_devices = get_device_usage_breakdown(week2_data)
    
    device_changes = {}
    for device in set(week1_devices.keys()).union(week2_devices.keys()):
        week1_usage = week1_devices.get(device, 0)
        week2_usage = week2_devices.get(device, 0)
        
        device_changes[device] = {
            "week1": week1_usage,
            "week2": week2_usage,
            "change": week2_usage - week1_usage,
            "change_pct": ((week2_usage - week1_usage) / week1_usage * 100) if week1_usage else float('inf')
        }
    
    return {
        "total_usage": {
            "week1": week1_total,
            "week2": week2_total,
            "change": week2_total - week1_total,
            "change_pct": (week2_total - week1_total) / week1_total * 100
        },
        "device_changes": device_changes,
        "week1_patterns": find_usage_patterns(week1_data),
        "week2_patterns": find_usage_patterns(week2_data)
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python parser.py <week1_file> <week2_file>")
        sys.exit(1)
        
    week1_data = load_power_data(sys.argv[1])
    week2_data = load_power_data(sys.argv[2])
    
    comparison = compare_weeks(week1_data, week2_data)
    print(json.dumps(comparison, indent=2))