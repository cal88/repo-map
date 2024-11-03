import os
import sys
import argparse
import asyncio
from src.repo_map.file_processing import (
    parse_gitignore,
    should_ignore,
    compute_file_hash,
    get_structure,
    get_module_docstring,
    get_imports,
    SUPPORTED_LANGUAGES
)
from src.repo_map.llm_interaction import enhance_repo_with_llm
from src.repo_map.cache_management import load_cache
from src.repo_map.output_generation import (
    print_tree,
    save_tree_map,
    save_pre_enhanced_map
)
import logging
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
import pathspec

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def summarize_repo(root_dir: str, cache_conn: sqlite3.Connection) -> List[Dict[Any, Any]]:
    summary = []
    ignore_patterns = parse_gitignore(root_dir)
    manual_ignore_patterns = ['.repo_map_structure.json', '.repo-map-cache.db']
    additional_patterns = ['*.pkl'] + manual_ignore_patterns
    combined_patterns = ignore_patterns + additional_patterns
    ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', combined_patterns)
    cursor = cache_conn.cursor()
    for root, dirs, files in os.walk(root_dir):
        relative_root = os.path.relpath(root, root_dir)
        if relative_root == '.':
            relative_root = ''
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(relative_root, d), ignore_spec)]
        if relative_root != '':
            dir_info = {
                'name': os.path.basename(root),
                'path': root,
                'level': relative_root.count(os.sep),
                'type': 'directory',
                'language': None
            }
            summary.append(dir_info)
        for file in sorted(files):
            full_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(full_path, root_dir)
            if should_ignore(relative_file_path, ignore_spec):
                continue
            _, ext = os.path.splitext(file)
            language = SUPPORTED_LANGUAGES.get(ext.lower())
            file_info = {
                'name': file,
                'path': full_path,
                'level': relative_file_path.count(os.sep),
                'type': 'file',
                'language': language
            }
            if language:
                file_hash = compute_file_hash(full_path)
                cursor.execute("SELECT hash, description, developer_consideration, imports, functions FROM cache WHERE path = ?", (full_path,))
                row = cursor.fetchone()
                if row and row[0] == file_hash:
                    file_info.update({
                        'description': row[1],
                        'developer_consideration': row[2],
                        'imports': json.loads(row[3]) if row[3] else [],
                        'functions': json.loads(row[4]) if row[4] else [],
                        'hash': file_hash
                    })
                else:
                    classes, functions_extracted, constants = get_structure(full_path, language)
                    module_doc = get_module_docstring(full_path, language)
                    imports = get_imports(full_path, language)
                    file_info.update({
                        'classes': classes,
                        'functions': functions_extracted,
                        'constants': constants,
                        'imports': imports,
                        'description': module_doc,
                        'hash': file_hash
                    })
            summary.append(file_info)
    return summary

async def main():
    parser = argparse.ArgumentParser(
        description=(
            "repo-map: A tool to generate a structured summary of a software repository.\n"
            "Note: Python has been tested to work. repo-map can parse various languages but \n"
            "has not been extensively tested. Please submit an issue on GitHub for any issues."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'repository_path',
        type=str,
        help='Path to the repository to be summarized.'
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Automatically accept the disclaimer and proceed without prompting.'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='anthropic/claude-3.5-sonnet',
        help='LLM model name to use for generating descriptions (default: anthropic/claude-3.5-sonnet).'
    )
    args = parser.parse_args()

    repo_path = args.repository_path
    if not os.path.isdir(repo_path):
        logger.error(f"Error: {repo_path} is not a valid directory")
        sys.exit(1)

    if not args.yes:
        if not confirm_disclaimer():
            logger.warning("Operation cancelled by the user.")
            sys.exit(0)

    cache_conn = load_cache(repo_path)
    logger.info("Generating repository summary...")
    summary = summarize_repo(repo_path, cache_conn)
    save_pre_enhanced_map(summary, os.path.join(repo_path, '.repo_map_structure.json'))
    
    await enhance_repo_with_llm(summary, cache_conn, model_name=args.model)
    
    cache_conn.close()
    directory_name = os.path.basename(os.path.normpath(repo_path))
    output_file_name = f"{directory_name}_repo_map.md"
    output_path = os.path.join(repo_path, output_file_name)
    save_tree_map(summary, repo_path, output_path)
    logger.info(f"Your repo-map has been saved to '{output_file_name}'.")

def confirm_disclaimer() -> bool:
    disclaimer_message = (
        "repo-map: A tool to generate a structured summary of a software repository.\n"
        "This tool uses the .gitignore in the target directory for files to not include in the repo map.\n"
        "Do you want to proceed? [y/n]: "
    )
    
    while True:
        user_input = input(disclaimer_message).strip().lower()
        if user_input in ('y', 'yes', ''):
            return True
        elif user_input in ('n', 'no'):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def run_main():
    asyncio.run(main())

if __name__ == "__main__":
    run_main()
