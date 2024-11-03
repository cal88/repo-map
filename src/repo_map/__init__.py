"""
repo-map: A tool to generate a structured summary of a software repository.
"""

from src.repo_map.repo_map import run_main
from src.repo_map.file_processing import (
    parse_gitignore,
    should_ignore,
    compute_file_hash,
    get_structure,
    get_module_docstring,
    get_imports,
    SUPPORTED_LANGUAGES
)
from src.repo_map.llm_interaction import (
    parse_llm_response,
    get_llm_descriptions,
    enhance_repo_with_llm
)
from src.repo_map.cache_management import load_cache
from src.repo_map.output_generation import (
    print_tree,
    save_tree_map,
    save_pre_enhanced_map
)

__version__ = "0.1.0"
