import os
import hashlib
import sqlite3
import logging
import pathspec
import ast
import re
from typing import Dict, List, Tuple, Any

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    '.py': 'Python',
    '.java': 'Java',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.cpp': 'C++',
    '.hpp': 'C++',
    '.h': 'C++',
    '.cs': 'C#',
    '.rb': 'Ruby',
    '.go': 'Go',
    '.php': 'PHP',
    '.txt': 'Text',
    '.md': 'Markdown',
    '.sh': 'Shell',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.json': 'JSON',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.less': 'LESS',
    '.sql': 'SQL',
    '.r': 'R',
    '.kt': 'Kotlin',
    '.swift': 'Swift',
    '.pl': 'Perl',
    '.asm': 'Assembly',
    '.clj': 'Clojure',
    '.groovy': 'Groovy',
    '.lua': 'Lua',
    '.pas': 'Pascal',
    '.scala': 'Scala',
    '.tsv': 'TSV',
    '.csv': 'CSV',
    '.xml': 'XML',
    '.ini': 'INI',
    '.cfg': 'Config',
    '.conf': 'Config',
    '.env': 'Config',
    '.envrc': 'Config',
    '.tf': 'Terraform',
    '.tfvars': 'Terraform',
    '.tfstate': 'Terraform',
    '.tfstate.backup': 'Terraform',
    '.hcl': 'Terraform',
    '.dockerfile': 'Docker',
    '.tfignore': 'Terraform',
    '.gitignore': 'Git',
    '.gitattributes': 'Git',
    '.db': 'Database',
    '.sqlite': 'Database',
    '.db3': 'Database',
    '.dbf': 'Database',
    '.dbx': 'Database',
    '.mdb': 'Database',
    '.accdb': 'Database',
    '.frm': 'Database',
    '.sqlitedb': 'Database',
    '.png': 'Image',
    '.jpg': 'Image',
    '.jpeg': 'Image',
    '.gif': 'Image',
    '.svg': 'Image',
    '.bmp': 'Image',
    '.ico': 'Image',
    '.tif': 'Image',
    '.tiff': 'Image',
    '.webp': 'Image',
    '.heic': 'Image',
    '.heif': 'Image',
    '.pdf': 'PDF',
    '.doc': 'Document',
    '.docx': 'Document',
    '.ppt': 'PowerPointPresentation',
    '.wav': 'Audio',
    '.mp3': 'Audio',
    '.mp4': 'Video',
    '.mov': 'Video',
    '.avi': 'Video',
    '.mkv': 'Video',
    '.webm': 'Video',
    '.flv': 'Video',
    '.wmv': 'Video',
    '.m4a': 'Audio',
    '.flac': 'Audio',
    '.ogg': 'Audio',
    '.opus': 'Audio',
    '.wma': 'Audio',
    '.aac': 'Audio',
    '.aiff': 'Audio',
    '.ape': 'Audio',
    '.alac': 'Audio',
    # Add more languages and extensions as needed
}

def parse_gitignore(root_dir: str) -> List[str]:
    ignore_patterns = []
    for dirpath, _, filenames in os.walk(root_dir):
        if '.gitignore' in filenames:
            gitignore_path = os.path.join(dirpath, '.gitignore')
            try:
                with open(gitignore_path, 'r') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    rel_path = os.path.relpath(dirpath, root_dir)
                    if rel_path != '.':
                        patterns = [os.path.join(rel_path, pattern) for pattern in patterns]
                    ignore_patterns.extend(patterns)
            except IOError as e:
                logger.error(f"Error reading .gitignore file at {gitignore_path}: {e}")
    return ignore_patterns

def should_ignore(path: str, ignore_spec: pathspec.PathSpec) -> bool:
    return ignore_spec.match_file(path)

def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except IOError as e:
        logger.error(f"Error reading file {file_path} for hashing: {e}")
        return ""

def get_python_structure(file_path: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read())
    except (SyntaxError, IOError) as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return {}, [], []
    
    classes = {}
    functions = []
    constants = []
    
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            classes[node.name] = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)
    
    return classes, functions, constants

def get_java_structure(file_path: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    classes = {}
    functions = []
    constants = []
    class_pattern = re.compile(r'class\s+(\w+)')
    method_pattern = re.compile(r'(public|protected|private)\s+\w+\s+(\w+)\s*\(')
    constant_pattern = re.compile(r'public\s+static\s+final\s+\w+\s+(\w+)\s*=')
    
    current_class = None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                class_match = class_pattern.search(line)
                if class_match:
                    current_class = class_match.group(1)
                    classes[current_class] = []
                    continue
                method_match = method_pattern.search(line)
                if method_match and current_class:
                    method_name = method_match.group(2)
                    classes[current_class].append(method_name)
                elif method_match and not current_class:
                    functions.append(method_match.group(2))
                constant_match = constant_pattern.search(line)
                if constant_match:
                    constants.append(constant_match.group(1))
    except IOError as e:
        logger.error(f"Error reading Java file {file_path}: {e}")
    
    return classes, functions, constants

def get_javascript_structure(file_path: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    classes = {}
    functions = []
    constants = []
    class_pattern = re.compile(r'class\s+(\w+)')
    method_pattern = re.compile(r'(\w+)\s*\(')
    function_pattern = re.compile(r'function\s+(\w+)\s*\(')
    constant_pattern = re.compile(r'const\s+(\w+)\s*=')
    
    current_class = None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                class_match = class_pattern.search(line)
                if class_match:
                    current_class = class_match.group(1)
                    classes[current_class] = []
                    continue
                method_match = method_pattern.search(line)
                if method_match and current_class:
                    method_name = method_match.group(1)
                    classes[current_class].append(method_name)
                else:
                    func_match = function_pattern.search(line)
                    if func_match:
                        functions.append(func_match.group(1))
                constant_match = constant_pattern.search(line)
                if constant_match:
                    constants.append(constant_match.group(1))
    except IOError as e:
        logger.error(f"Error reading JavaScript file {file_path}: {e}")
    
    return classes, functions, constants

def get_csharp_structure(file_path: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    classes = {}
    functions = []
    constants = []
    class_pattern = re.compile(r'class\s+(\w+)')
    method_pattern = re.compile(r'(public|protected|private)\s+\w+\s+(\w+)\s*\(')
    constant_pattern = re.compile(r'public\s+const\s+\w+\s+(\w+)\s*=')
    
    current_class = None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                class_match = class_pattern.search(line)
                if class_match:
                    current_class = class_match.group(1)
                    classes[current_class] = []
                    continue
                method_match = method_pattern.search(line)
                if method_match and current_class:
                    method_name = method_match.group(2)
                    classes[current_class].append(method_name)
                elif method_match and not current_class:
                    functions.append(method_match.group(2))
                constant_match = constant_pattern.search(line)
                if constant_match:
                    constants.append(constant_match.group(1))
    except IOError as e:
        logger.error(f"Error reading C# file {file_path}: {e}")
    
    return classes, functions, constants

def get_module_docstring(file_path: str, language: str) -> str:
    if language == 'Python':
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                docstring = ast.get_docstring(tree)
                return docstring if docstring else ""
        except (SyntaxError, IOError) as e:
            logger.error(f"Error getting docstring from {file_path}: {e}")
            return ""
    elif language in ['Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'PHP']:
        comment_pattern = re.compile(r'^\s*//\s*(.*)|^\s*/\*\*\s*(.*?)\s*\*/', re.MULTILINE)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                matches = comment_pattern.findall(content)
                comments = [m[0] or m[1] for m in matches if m[0] or m[1]]
                return ' '.join(comments).strip()
        except IOError as e:
            logger.error(f"Error reading comments from {file_path}: {e}")
            return ""
    else:
        return ""

def get_imports(file_path: str, language: str) -> List[str]:
    imports = []
    if language == 'Python':
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
        except (SyntaxError, IOError) as e:
            logger.error(f"Error parsing imports from {file_path}: {e}")
            return []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Add the alias name if it exists, otherwise use the original name
                    imports.append(alias.asname if alias.asname else alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    # Add the alias name if it exists, otherwise use the qualified name
                    imports.append(alias.asname if alias.asname else f"{module}.{alias.name}")
    elif language in ['Java', 'JavaScript', 'TypeScript', 'C#', 'PHP']:
        import_patterns = {
            'Java': re.compile(r'import\s+([\w\.]+);'),
            'JavaScript': re.compile(r'import\s+.*?\s+from\s+[\'"]([\w\.\/]+)[\'"];'),
            'TypeScript': re.compile(r'import\s+.*?\s+from\s+[\'"]([\w\.\/]+)[\'"];'),
            'C#': re.compile(r'using\s+([\w\.]+);'),
            'PHP': re.compile(r'use\s+([\w\\]+);'),
        }
        pattern = import_patterns.get(language)
        if pattern:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        match = pattern.search(line)
                        if match:
                            imports.append(match.group(1))
            except IOError as e:
                logger.error(f"Error reading imports from {file_path}: {e}")
    return imports

def get_constants(file_path: str, language: str) -> List[str]:
    constants = []
    if language == 'Python':
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id.isupper():
                                constants.append(target.id)
        except (SyntaxError, IOError) as e:
            logger.error(f"Error parsing constants from {file_path}: {e}")
    elif language == 'Java':
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                constants = re.findall(r'public\s+static\s+final\s+\w+\s+(\w+)\s*=', content)
        except IOError as e:
            logger.error(f"Error reading constants from {file_path}: {e}")
    return constants

def get_structure(file_path: str, language: str) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    if language == 'Python':
        return get_python_structure(file_path)
    elif language == 'Java':
        return get_java_structure(file_path)
    elif language in ['JavaScript', 'TypeScript']:
        return get_javascript_structure(file_path)
    elif language == 'C#':
        return get_csharp_structure(file_path)
    else:
        return {}, [], []
