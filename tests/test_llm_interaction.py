import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Tuple, Optional

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repo_map.llm_interaction import (
    parse_llm_response,
    get_llm_descriptions
)

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

class TestLLMInteraction(unittest.TestCase):
    def setUp(self):
        # Use existing test_output directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_output')

    def test_parse_llm_response(self):
        # Test parsing valid LLM response
        content = """
        Description: This is a test file description
        Developer Consideration: "This is a test consideration"
        """
        file_info: Dict[str, Any] = {}
        parse_llm_response(content, file_info)

        # Save the parsed response to a file
        output_file = os.path.join(self.test_dir, 'llm_response.txt')
        with open(output_file, 'w') as f:
            f.write(f"Description: {file_info.get('description', '')}\n")
            f.write(f"Developer Consideration: {file_info.get('developer_consideration', '')}\n")

        self.assertEqual(file_info['description'], "This is a test file description")
        self.assertEqual(file_info['developer_consideration'], "This is a test consideration")

        # Test parsing incomplete response
        content = "Description: Only description present"
        file_info = {}
        parse_llm_response(content, file_info)

        # Save the incomplete response
        output_file = os.path.join(self.test_dir, 'llm_response_incomplete.txt')
        with open(output_file, 'w') as f:
            f.write(f"Description: {file_info.get('description', '')}\n")
            f.write(f"Developer Consideration: {file_info.get('developer_consideration', '')}\n")

        self.assertEqual(file_info['description'], "Only description present")
        self.assertNotIn('developer_consideration', file_info)

        # Test parsing malformed response
        content = "Invalid response format"
        file_info = {}
        parse_llm_response(content, file_info)

        # Save the malformed response
        output_file = os.path.join(self.test_dir, 'llm_response_malformed.txt')
        with open(output_file, 'w') as f:
            f.write(f"Description: {file_info.get('description', '')}\n")
            f.write(f"Developer Consideration: {file_info.get('developer_consideration', '')}\n")

        self.assertNotIn('description', file_info)
        self.assertNotIn('developer_consideration', file_info)

    @async_test
    async def test_get_llm_descriptions(self):
        test_structure = [
            {
                "name": "test.py",
                "type": "file",
                "language": "Python",
                "imports": ["os"],
                "functions": ["test_func"],
                "level": 0
            }
        ]
        test_file = test_structure[0]

        # Test with no LLM response (simulating no API key)
        await get_llm_descriptions(test_structure, 0, test_file, "test-model")

        # Save the test result
        output_file = os.path.join(self.test_dir, 'llm_descriptions.txt')
        with open(output_file, 'w') as f:
            f.write(f"File: {test_file['name']}\n")
            f.write(f"Description: {test_file.get('description', 'None')}\n")
            f.write(f"Developer Consideration: {test_file.get('developer_consideration', 'None')}\n")

        self.assertNotIn('description', test_file)
        self.assertNotIn('developer_consideration', test_file)

if __name__ == '__main__':
    unittest.main()
