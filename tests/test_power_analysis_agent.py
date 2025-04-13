"""
Tests for the Power Analysis Agent.
"""
import os
import sys
import unittest
import json
from pathlib import Path

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.power_analysis_agent import create_power_analysis_agent
from utils.parser import load_power_data, compare_weeks


class TestPowerAnalysisAgent(unittest.TestCase):
    """Test cases for the Power Analysis Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.week1_path = str(self.data_dir / "example_week1.json")
        self.week2_path = str(self.data_dir / "example_week2.json")
        
        # Ensure test data files exist
        self.assertTrue(os.path.exists(self.week1_path), f"Test file not found: {self.week1_path}")
        self.assertTrue(os.path.exists(self.week2_path), f"Test file not found: {self.week2_path}")
    
    def test_data_loading(self):
        """Test that data files can be loaded correctly."""
        week1_data = load_power_data(self.week1_path)
        week2_data = load_power_data(self.week2_path)
        
        # Verify basic structure
        self.assertIn("metadata", week1_data)
        self.assertIn("daily_usage", week1_data)
        self.assertEqual(7, len(week1_data["daily_usage"]))  # 7 days in a week
        
        self.assertIn("metadata", week2_data)
        self.assertIn("daily_usage", week2_data)
        self.assertEqual(7, len(week2_data["daily_usage"]))  # 7 days in a week
    
    def test_data_comparison(self):
        """Test that weeks can be compared."""
        week1_data = load_power_data(self.week1_path)
        week2_data = load_power_data(self.week2_path)
        
        comparison = compare_weeks(week1_data, week2_data)
        
        # Check basic structure of comparison results
        self.assertIn("total_usage", comparison)
        self.assertIn("device_changes", comparison)
        self.assertIn("week1_patterns", comparison)
        self.assertIn("week2_patterns", comparison)
    
    def test_agent_creation(self):
        """Test that the agent can be created."""
        agent = create_power_analysis_agent()
        self.assertIsNotNone(agent)
    
    def test_agent_output_structure(self):
        """Test that the agent produces output (structure only, not content)."""
        # Skip this test if OPENAI_API_KEY is not available
        if not os.environ.get("OPENAI_API_KEY"):
            self.skipTest("OPENAI_API_KEY environment variable not set")
            
        agent = create_power_analysis_agent()
        result = agent(self.week1_path, self.week2_path)
        
        # Check that result is a non-empty string
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()