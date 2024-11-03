import os
import sys
import unittest
import json
import logging
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repo_map.output_generation import (
    print_tree,
    save_tree_map,
    save_pre_enhanced_map
)

class TestOutputGeneration(unittest.TestCase):
    def setUp(self):
        # Use existing test_output directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        
        self.test_structure = [
            {
                'name': 'src',
                'path': '/test/src',
                'level': 0,
                'type': 'directory',
                'language': None
            },
            {
                'name': 'main.py',
                'path': '/test/src/main.py',
                'level': 1,
                'type': 'file',
                'language': 'Python',
                'description': 'Main entry point',
                'developer_consideration': 'Contains global state',
                'imports': ['os', 'sys'],
                'functions': ['main', 'setup']
            },
            {
                'name': 'utils',
                'path': '/test/src/utils',
                'level': 1,
                'type': 'directory',
                'language': None
            },
            {
                'name': 'helpers.py',
                'path': '/test/src/utils/helpers.py',
                'level': 2,
                'type': 'file',
                'language': 'Python',
                'description': 'Utility functions',
                'developer_consideration': 'Uses caching',
                'imports': ['json'],
                'functions': ['helper1', 'helper2']
            }
        ]

        # Set up logging capture
        self.log_output = StringIO()
        self.log_handler = logging.StreamHandler(self.log_output)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.WARNING)

    def tearDown(self):
        # Clean up logging only
        logging.getLogger().removeHandler(self.log_handler)
        self.log_output.close()

    def test_save_pre_enhanced_map(self):
        output_path = os.path.join(self.test_dir, '.repo_map_structure.json')
        save_pre_enhanced_map(self.test_structure, output_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Verify content
        with open(output_path, 'r') as f:
            saved_structure = json.load(f)
        
        self.assertEqual(len(saved_structure), len(self.test_structure))
        self.assertEqual(saved_structure[0]['name'], 'src')
        self.assertEqual(saved_structure[1]['name'], 'main.py')
        self.assertEqual(saved_structure[1]['description'], 'Main entry point')

    def test_save_tree_map(self):
        output_path = os.path.join(self.test_dir, 'repo_map.md')
        save_tree_map(self.test_structure, self.test_dir, output_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Read the content and verify structure
        with open(output_path, 'r') as f:
            content = f.read()

        # Check for key elements in the output
        self.assertIn('# Repository Map', content)
        self.assertIn('src/', content)
        self.assertIn('main.py (Python)', content)
        self.assertIn('Description: Main entry point', content)
        self.assertIn('Developer Consideration: "Contains global state"', content)
        self.assertIn('utils/', content)
        self.assertIn('helpers.py (Python)', content)

    def test_print_tree(self):
        # Clear any previous log output
        self.log_output.seek(0)
        self.log_output.truncate()

        # Call print_tree
        print_tree(self.test_structure)
        
        # Get the log output
        log_content = self.log_output.getvalue()

        # Verify the tree structure in the output
        self.assertIn('src/', log_content)
        self.assertIn('main.py (Python)', log_content)
        self.assertIn('Description: Main entry point', log_content)
        self.assertIn('Developer Consideration: "Contains global state"', log_content)
        self.assertIn('utils/', log_content)
        self.assertIn('helpers.py (Python)', log_content)

if __name__ == '__main__':
    unittest.main()
