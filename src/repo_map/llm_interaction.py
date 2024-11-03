import os
import json
import asyncio
import re
from typing import List, Dict, Any, Optional
import sqlite3
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_llm_descriptions(structure: List[Dict[str, Any]], file_index: int, file: Dict[str, Any], model: str, max_retries: int = 3) -> None:
    """
    Get descriptions for a file using LLM. If no API key is available, skips enhancement.
    This function is designed to work without LLM when no API key is present.
    """
    # Skip LLM enhancement if no API key is available
    logger.warning(f"No response received for {file['name']}, skipping LLM enhancement")
    return

def parse_llm_response(content: str, file: Dict[str, Any]) -> None:
    """
    Parse LLM response and update file info with description and developer consideration.
    """
    file_desc_pattern = r"Description:\s*(.*)"
    considerations_pattern = r"Developer Consideration:\s*\"(.*?)\""

    file_desc_match = re.search(file_desc_pattern, content)
    if file_desc_match:
        file['description'] = file_desc_match.group(1).strip()

    considerations_match = re.search(considerations_pattern, content)
    if considerations_match:
        file['developer_consideration'] = considerations_match.group(1).strip()

async def enhance_repo_with_llm(structure: List[Dict[str, Any]], cache_conn: sqlite3.Connection, model_name: str) -> None:
    """
    Enhance repository structure with LLM-generated descriptions.
    If no API key is available, skips enhancement.
    """
    logger.info("No valid API key found. Skipping LLM enhancement.")
    cursor = cache_conn.cursor()
    
    for index, item in enumerate(structure):
        if item['type'] == 'file' and (item.get('imports') or item.get('functions')):
            cursor.execute("SELECT hash FROM cache WHERE path = ?", (item['path'],))
            row = cursor.fetchone()
            if not row or row[0] != item.get('hash', ''):
                await get_llm_descriptions(structure, index, item, model=model_name)
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
