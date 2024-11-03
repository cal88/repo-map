import os
import sys
import unittest
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repo_map.file_processing import (
    parse_gitignore,
    should_ignore,
    compute_file_hash,
    get_python_structure,
    get_java_structure,
    get_javascript_structure,
    get_module_docstring,
    get_imports,
    SUPPORTED_LANGUAGES
)
import pathspec

class TestFileProcessing(unittest.TestCase):
    def setUp(self):
        # Use existing test_output directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_output')

    def test_gitignore_parsing(self):
        # Create a test .gitignore file
        gitignore_content = """
*.pyc
__pycache__/
.env
.vscode/
"""
        gitignore_path = os.path.join(self.test_dir, '.gitignore')
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)

        patterns = parse_gitignore(self.test_dir)
        self.assertIn('*.pyc', patterns)
        self.assertIn('__pycache__/', patterns)
        self.assertIn('.env', patterns)
        self.assertIn('.vscode/', patterns)

    def test_should_ignore(self):
        patterns = ['*.pyc', '__pycache__/', '.env', '.vscode/']
        ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)

        # Test files that should be ignored
        self.assertTrue(should_ignore('test.pyc', ignore_spec))
        self.assertTrue(should_ignore('__pycache__/cache.py', ignore_spec))
        self.assertTrue(should_ignore('.env', ignore_spec))
        self.assertTrue(should_ignore('.vscode/settings.json', ignore_spec))

        # Test files that should not be ignored
        self.assertFalse(should_ignore('test.py', ignore_spec))
        self.assertFalse(should_ignore('src/main.py', ignore_spec))
        self.assertFalse(should_ignore('README.md', ignore_spec))

    def test_compute_file_hash(self):
        # Create a test file with known content
        test_file = os.path.join(self.test_dir, 'test.txt')
        content = "Hello, World!"
        with open(test_file, 'w') as f:
            f.write(content)

        # Compute hash and verify it's not empty
        file_hash = compute_file_hash(test_file)
        self.assertTrue(file_hash)
        self.assertEqual(len(file_hash), 64)  # SHA-256 hash length

        # Verify hash changes with content
        with open(test_file, 'w') as f:
            f.write("Different content")
        new_hash = compute_file_hash(test_file)
        self.assertNotEqual(file_hash, new_hash)

    def test_python_structure(self):
        # Create a test Python file
        python_content = """\"\"\"Module docstring\"\"\"
import os
import sys
from typing import List

CONSTANT = 42

class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        pass

def function1():
    pass

def function2():
    pass
"""
        python_file = os.path.join(self.test_dir, 'test.py')
        with open(python_file, 'w') as f:
            f.write(python_content)

        classes, functions, constants = get_python_structure(python_file)
        
        # Verify class and methods
        self.assertIn('TestClass', classes)
        self.assertIn('method1', classes['TestClass'])
        self.assertIn('method2', classes['TestClass'])

        # Verify standalone functions
        self.assertIn('function1', functions)
        self.assertIn('function2', functions)

        # Verify constants
        self.assertIn('CONSTANT', constants)

    def test_module_docstring(self):
        # Create a test Python file with docstring
        python_content = """\"\"\"
This is a test module docstring.
It should be extracted correctly.
\"\"\"
def test():
    pass
"""
        python_file = os.path.join(self.test_dir, 'test_docstring.py')
        with open(python_file, 'w') as f:
            f.write(python_content)

        docstring = get_module_docstring(python_file, 'Python')
        self.assertIn('test module docstring', docstring)

    def test_python_imports(self):
        # Create a test Python file with imports
        python_content = """\"\"\"Test module\"\"\"
import os
import sys as system
from typing import List, Dict
from pathlib import Path
"""
        python_file = os.path.join(self.test_dir, 'test_imports.py')
        with open(python_file, 'w') as f:
            f.write(python_content)

        imports = get_imports(python_file, 'Python')
        self.assertIn('os', imports)
        self.assertIn('system', imports)
        self.assertIn('typing.List', imports)
        self.assertIn('typing.Dict', imports)
        self.assertIn('pathlib.Path', imports)

    def test_supported_languages(self):
        # Verify common extensions are supported
        self.assertEqual(SUPPORTED_LANGUAGES.get('.py'), 'Python')
        self.assertEqual(SUPPORTED_LANGUAGES.get('.java'), 'Java')
        self.assertEqual(SUPPORTED_LANGUAGES.get('.js'), 'JavaScript')
        self.assertEqual(SUPPORTED_LANGUAGES.get('.jsx'), 'JavaScript')
        self.assertEqual(SUPPORTED_LANGUAGES.get('.ts'), 'TypeScript')
        self.assertEqual(SUPPORTED_LANGUAGES.get('.cpp'), 'C++')

if __name__ == '__main__':
    unittest.main()
