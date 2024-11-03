import os
import json
import asyncio
import re
from typing import List, Dict, Any, Optional
import sqlite3
import logging
import aiohttp
from dotenv import load_dotenv

def load_env_file():
    """Manually load .env file"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env_file()

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_llm_descriptions(structure: List[Dict[str, Any]], file_index: int, file: Dict[str, Any], model: str, max_retries: int = 3) -> None:
    """
    Get descriptions for a file using LLM via OpenRouter API.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.warning(f"No OpenRouter API key found, skipping LLM enhancement for {file['name']}")
        return

    # Debug log for API key (first 10 chars only for security)
    logger.warning(f"Using API key starting with: {api_key[:10]}...")

    # Prepare the content for LLM
    content = f"File: {file['name']}\n"
    if file.get('imports'):
        content += "Imports:\n" + "\n".join([f"- {imp}" for imp in file['imports']]) + "\n"
    if file.get('functions'):
        content += "Functions:\n" + "\n".join([f"- {func}" for func in file['functions']]) + "\n"
    if file.get('classes'):
        content += "Classes:\n" + "\n".join([f"- {cls}" for cls in file['classes']]) + "\n"
    if file.get('constants'):
        content += "Constants:\n" + "\n".join([f"- {const}" for const in file['constants']]) + "\n"
    if not any([file.get('imports'), file.get('functions'), file.get('classes'), file.get('constants')]):
        content += "Note: This is an empty or utility Python file.\n"

    prompt = f"""Analyze this Python file and provide:
1. A concise description of its purpose and functionality based on its name, location, and available code elements
2. A key developer consideration for maintaining or modifying this file

Format your response exactly as:
Description: [your description]
Developer Consideration: "[your consideration]"

File details:
{content}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/repo-map",
        "X-Title": "repo-map"
    }

    # Debug log for headers (excluding full API key)
    safe_headers = headers.copy()
    safe_headers["Authorization"] = f"Bearer {api_key[:10]}..."
    logger.warning(f"Request headers: {json.dumps(safe_headers, indent=2)}")

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "top_p": 1,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "repetition_penalty": 1,
                        "top_k": 0
                    },
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        parse_llm_response(content, file)
                        return
                    else:
                        error_text = await response.text()
                        logger.warning(f"API request failed with status {response.status}: {error_text}")
                        if attempt == max_retries - 1:
                            logger.warning(f"Max retries reached for {file['name']}, skipping LLM enhancement")
                            return
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.warning(f"Error during API request for {file['name']}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.warning(f"Max retries reached for {file['name']}, skipping LLM enhancement")
                    return
                await asyncio.sleep(2 ** attempt)

def parse_llm_response(content: str, file: Dict[str, Any]) -> None:
    """
    Parse LLM response and update file info with description and developer consideration.
    """
    file_desc_pattern = r"Description:\s*(.*?)(?=Developer Consideration:|$)"
    considerations_pattern = r"Developer Consideration:\s*\"(.*?)\""

    file_desc_match = re.search(file_desc_pattern, content, re.DOTALL)
    if file_desc_match:
        file['description'] = file_desc_match.group(1).strip()

    considerations_match = re.search(considerations_pattern, content)
    if considerations_match:
        file['developer_consideration'] = considerations_match.group(1).strip()

async def enhance_repo_with_llm(structure: List[Dict[str, Any]], cache_conn: sqlite3.Connection, model_name: str) -> None:
    """
    Enhance repository structure with LLM-generated descriptions.
    Uses caching to avoid redundant API calls.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.warning("No OpenRouter API key found in environment. Skipping LLM enhancement.")
        return
    
    # Debug log for API key
    logger.warning(f"Using API key starting with: {api_key[:10]}...")

    cursor = cache_conn.cursor()
    
    for index, item in enumerate(structure):
        if item['type'] == 'file' and item.get('language') == 'Python':  # Process all Python files
            cursor.execute("SELECT hash, description, developer_consideration FROM cache WHERE path = ?", (item['path'],))
            row = cursor.fetchone()
            
            if row and row[0] == item.get('hash', ''):
                # Use cached data
                item['description'] = row[1]
                item['developer_consideration'] = row[2]
            else:
                # Get new descriptions from LLM
                await get_llm_descriptions(structure, index, item, model=model_name)
                
                # Update cache
                cursor.execute("""
                    INSERT OR REPLACE INTO cache (
                        path, hash, description, developer_consideration, imports, functions
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item['path'],
                    item.get('hash', ''),
                    item.get('description', ''),
                    item.get('developer_consideration', ''),
                    json.dumps(item.get('imports', [])),
                    json.dumps(item.get('functions', []))
                ))
                cache_conn.commit()
