import os
import json
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_tree(structure: List[Dict[str, Any]]):
    def print_item(item: Dict[str, Any], prefix: str, is_last: bool):
        connector = '└── ' if is_last else '├── '
        if item['type'] == 'directory':
            logger.warning(f"{prefix}{connector}{item['name']}/")
            new_prefix = prefix + ('    ' if is_last else '│   ')
            return new_prefix  
        else:
            language = item.get('language', 'None')
            logger.warning(f"{prefix}{connector}{item['name']} ({language})")

            new_prefix = prefix + ('    ' if is_last else '│   ')

            if 'description' in item and item['description']:
                logger.warning(f"{new_prefix}├── Description: {item['description']}")
            
            if 'developer_consideration' in item and item['developer_consideration']:
                logger.warning(f"{new_prefix}├── Developer Consideration: \"{item['developer_consideration']}\"")

            if 'imports' in item and item['imports']:
                logger.warning(f"{new_prefix}├── Imports: {item['imports']}")

            if 'functions' in item and item['functions']:
                logger.warning(f"{new_prefix}├── Functions: {item['functions']}")

    logger.warning("/ (Root Directory)")
    for i, item in enumerate(structure):
        prefix = '│   ' * item['level']
        is_last = i == len(structure) - 1
        print_item(item, prefix, is_last)
    logger.warning("└────────────── ")

def save_tree_map(structure: List[Dict[str, Any]], repo_root: str, output_path: str):
    def write_item(item: Dict[str, Any], prefix: str, is_last: bool, file_handle):
        connector = '└── ' if is_last else '├── '
        if item['type'] == 'directory':
            file_handle.write(f"{prefix}{connector}{item['name']}/\n")
            return  
        else:
            language = item.get('language', 'None')
            file_handle.write(f"{prefix}{connector}{item['name']} ({language})\n")

            new_prefix = prefix + ('    ' if is_last else '│   ')

            if 'description' in item and item['description']:
                file_handle.write(f"{new_prefix}├── Description: {item['description']}\n")

            if 'developer_consideration' in item and item['developer_consideration']:
                file_handle.write(f"{new_prefix}├── Developer Consideration: \"{item['developer_consideration']}\"\n")

            if 'imports' in item and item['imports']:
                file_handle.write(f"{new_prefix}├── Imports: {item['imports']}\n")

            if 'functions' in item and item['functions']:
                file_handle.write(f"{new_prefix}├── Functions: {item['functions']}\n")

    repo_name = os.path.basename(os.path.normpath(repo_root))
    try:
        with open(output_path, 'w', encoding='utf-8') as file_handle:
            file_handle.write("# Repository Map\n\n")
            file_handle.write("```markdown\n")
            file_handle.write(f"/ ({repo_name})\n")
            for i, item in enumerate(structure):
                prefix = '│   ' * item['level']
                is_last = i == len(structure) - 1
                write_item(item, prefix, is_last, file_handle)
            file_handle.write("└────────────── \n")
            file_handle.write("```\n")
        logger.warning(f"Repository map saved to '{output_path}'.")
    except IOError as e:
        logger.error(f"Error saving repository map: {e}")

def save_pre_enhanced_map(structure: List[Dict[str, Any]], output_path: str = '.repo_map_structure.json'):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=4)
        logger.warning(f"repo-map structure saved to '{output_path}'.")
    except IOError as e:
        logger.error(f"Error saving .repo_map_structure.json: {e}")
