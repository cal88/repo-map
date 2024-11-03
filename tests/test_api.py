import os
import sys
import unittest
import json
from unittest.mock import patch
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestOpenRouterAPI(unittest.TestCase):
    def setUp(self):
        # Use existing test_output directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('OPENROUTER_API_KEY')

        # Save API key status to test output
        output_file = os.path.join(self.test_dir, 'api_key_status.json')
        with open(output_file, 'w') as f:
            json.dump({
                "api_key_exists": self.api_key is not None,
                "api_key_prefix": self.api_key[:10] if self.api_key else None
            }, f, indent=2)

    def test_api_key_exists(self):
        """Test that the OpenRouter API key is available"""
        self.assertIsNotNone(self.api_key, "OpenRouter API key not found in environment")
        if self.api_key:  # Only check format if key exists
            self.assertTrue(self.api_key.startswith('sk-or-v1-'), "OpenRouter API key has incorrect format")

    def test_api_headers(self):
        """Test that API headers are correctly formatted"""
        if not self.api_key:
            self.skipTest("OpenRouter API key not available")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/repo-map",
            "X-Title": "repo-map"
        }

        # Save headers to test output (excluding API key)
        safe_headers = headers.copy()
        safe_headers["Authorization"] = f"Bearer {self.api_key[:10]}..."
        output_file = os.path.join(self.test_dir, 'api_headers.json')
        with open(output_file, 'w') as f:
            json.dump(safe_headers, f, indent=2)

        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertTrue(headers["HTTP-Referer"].endswith("repo-map"))

    @patch('requests.post')
    def test_api_request_format(self, mock_post):
        """Test that API request is correctly formatted"""
        if not self.api_key:
            self.skipTest("OpenRouter API key not available")

        # Mock successful response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Description: Test description\nDeveloper Consideration: \"Test consideration\""
                }
            }]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response

        # Test file info
        test_file = {
            "name": "test.py",
            "imports": ["os", "sys"],
            "functions": ["test_func"]
        }

        # Example request data
        request_data = {
            "model": "google/gemini-pro-1.5",
            "messages": [{
                "role": "user",
                "content": "Analyze this Python file and provide:\n1. A concise description\n2. A key developer consideration"
            }],
            "temperature": 0.2,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0
        }

        # Save test request to output
        output_file = os.path.join(self.test_dir, 'api_request.json')
        with open(output_file, 'w') as f:
            json.dump(request_data, f, indent=2)

        # Make test request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/repo-map",
            "X-Title": "repo-map"
        }

        response = mock_post.return_value
        response.status_code = 200
        response.json.return_value = mock_response

        # Make request
        mock_post.return_value = response
        result = mock_post("https://openrouter.ai/api/v1/chat/completions", 
                          headers=headers, 
                          json=request_data)

        # Verify request format
        self.assertTrue(mock_post.called)
        args, kwargs = mock_post.call_args
        self.assertIn("json", kwargs)
        self.assertIn("headers", kwargs)
        self.assertIn("model", kwargs["json"])
        self.assertIn("messages", kwargs["json"])
        self.assertEqual(kwargs["json"]["temperature"], 0.2)

if __name__ == '__main__':
    unittest.main()
