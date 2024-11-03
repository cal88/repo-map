# Technology Stack: repo-map

## Programming Languages:

- Python: Core language for the application.

## Frameworks/Libraries:

- `aiohttp`: Asynchronous HTTP client for making API requests.
- `requests`:  Synchronous HTTP client (used for fallback or specific needs).
- `sqlite3`:  SQLite database for caching LLM responses.
- `pathspec`: For parsing `.gitignore` files.
- `argparse`: For command-line argument parsing.
- `tqdm`: For progress bars.
- `ast`: For abstract syntax tree parsing (Python code analysis).
- `re`: For regular expression operations.

## AI Services:

- OpenRouter:  LLM API for generating code descriptions.  (API key management via `.env` file).

## Other:

- Markdown: Used for documentation and output.
- JSON: Used for data serialization.
