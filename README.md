# 🗺️ repo-map
repo-map is an advanced tool for generating comprehensive, AI-enhanced summaries of software repositories. It provides developers with valuable insights into project structures, file purposes, and potential considerations across various programming languages. Using efficient caching, repo-map only processes files that have changed since the last run, making it ideal for continuous use in evolving projects. This tool not only aids in understanding and documenting codebases but can also assist LLM agents in writing accurate and functional code within your existing project structure.

## 🌟 Features
- 📊 Generates detailed repository structure summaries
- 🧠 AI-powered enhancements:
  - 💡 Developer considerations for potential issues or unique aspects
  - 🗣️ Concise explanations of file purposes and functionality
  - 🔍 Insights into code structure and organization
- 🌐 Analyzes code structure across multiple programming languages
- 🚀 Supports various file types including Python, Java, JavaScript, TypeScript, and more
- 💾 Caching mechanism using SQLite for efficient processing of unchanged files
- 🌳 Tree-like visualization of the repository structure
- 📝 Markdown output for easy sharing and documentation
- 🔒 Respects .gitignore files (including nested ones) within the target directory for file exclusion
- 🚦 Implements rate limiting and exponential backoff for LLM API calls
- ⚡ Asynchronous processing for improved performance
- 🧪 Comprehensive test suite with preserved test outputs

## 🛠️ Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repo-map.git
cd repo-map
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenRouter API key:
```bash
export OPENROUTER_API_KEY=your_api_key_here
# Or create a .env file with:
# OPENROUTER_API_KEY=your_api_key_here
```

## 🚀 Usage

Run repo-map using the Python module syntax:

```bash
# Basic usage
python -m src.repo_map.repo_map <repository_path>

# Auto-accept disclaimer (skip prompt)
python -m src.repo_map.repo_map <repository_path> -y

# Use a specific LLM model
python -m src.repo_map.repo_map <repository_path> --model anthropic/claude-3-opus
```

For example, to analyze the current directory:
```bash
python -m src.repo_map.repo_map .
```

The script will generate:
1. A `.repo_map_structure.json` file containing the raw repository data
2. A markdown file named `<directory>_repo_map.md` with the formatted repository map

Note: LLM enhancement requires an OpenRouter API key. Without one, the script will still work but skip the LLM descriptions.

## 🧪 Testing

The project includes a comprehensive test suite covering all major components:

```bash
# Run all tests
python -m tests.run_tests

# Run specific test files
python -m unittest tests.test_file_processing
python -m unittest tests.test_cache_management
python -m unittest tests.test_llm_interaction
python -m unittest tests.test_output_generation
python -m unittest tests.test_api
```

Test outputs are preserved in `tests/test_output/` for debugging and analysis:
- Cache files (.repo-map-cache.db)
- Structure files (.repo_map_structure.json)
- Tree maps (repo_map.md)
- LLM responses (llm_response*.txt)
- API test files (api_*.json)

## 📁 Project Structure

```
repo-map/
├── src/                    # Source code
│   └── repo_map/          # Main package
│       ├── __init__.py    # Package initialization
│       ├── repo_map.py    # Main entry point
│       ├── file_processing.py    # File analysis
│       ├── llm_interaction.py    # LLM API handling
│       ├── cache_management.py   # SQLite caching
│       └── output_generation.py  # Output formatting
├── tests/                 # Test suite
│   ├── test_output/      # Preserved test outputs
│   ├── run_tests.py      # Test runner
│   ├── test_api.py       # API integration tests
│   ├── test_cache_management.py
│   ├── test_file_processing.py
│   ├── test_llm_interaction.py
│   └── test_output_generation.py
├── project_docs/         # Project documentation
├── requirements.txt      # Direct dependencies
├── pyproject.toml       # Package metadata and build config
└── README.md           # This file
```

## 🐍 Example Output

Here's an example of a repo-map output:

```markdown
/ (repo-map)
├── src/
│   ├── repo_map/
│   │   ├── __init__.py (Python)
│   │   │   ├── Description: Entry point for the repo-map package
│   │   │   ├── Imports: [repo_map.core, repo_map.utils]
│   │   ├── file_processing.py (Python)
│   │   │   ├── Description: Handles file system operations and code analysis
│   │   │   ├── Developer Consideration: "Implements caching for efficient processing"
│   │   │   ├── Functions: [parse_gitignore, compute_file_hash, get_structure]
│   │   ├── llm_interaction.py (Python)
│   │   │   ├── Description: Manages LLM API interactions
│   │   │   ├── Developer Consideration: "Implements rate limiting for API calls"
├── tests/
│   ├── test_file_processing.py (Python)
│   ├── test_llm_interaction.py (Python)
└──────────────
```

## 🔧 Requirements
- Python 3.7+
- Dependencies (see requirements.txt):
  - aiohttp
  - pathspec
  - tqdm
  - certifi
  - python-dotenv

## 🧩 How It Works
1. 📂 Walks through the repository directory structure
2. 📝 Analyzes file contents and extracts key information (imports, functions, classes)
3. 🤖 Utilizes an LLM (via OpenRouter) to generate descriptions and developer considerations
4. 🗃️ Caches results in SQLite for efficient processing of unchanged files
5. 📊 Generates a comprehensive tree-like structure of the repository
6. 💾 Saves the output as a Markdown file for easy viewing and sharing

## 📋 Additional Notes
- The tool supports multiple programming languages through the `SUPPORTED_LANGUAGES` configuration
- Results are cached in `.repo-map-cache.db` for efficient subsequent runs
- The tool respects .gitignore patterns and includes additional manual ignore patterns
- SSL verification is handled using the certifi library for secure API communications
- Test outputs are preserved for debugging and analysis

## 🛡️ License
This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenRouter API key
4. Run tests to verify setup: `python -m tests.run_tests`

### Running Tests
The project uses Python's unittest framework. Tests are organized by component:
- test_file_processing.py: File system operations
- test_cache_management.py: Cache operations
- test_llm_interaction.py: LLM integration
- test_output_generation.py: Output formatting
- test_api.py: OpenRouter API integration

Test outputs are preserved in tests/test_output/ for debugging.

## 📞 Support
If you encounter any problems or have questions, please open an issue in the GitHub repository.

## ⚠️ Disclaimer
By using this tool, you acknowledge that files will be sent to the OpenRouter LLM for processing. Ensure you have the necessary permissions and consider any sensitive information in your repository.
