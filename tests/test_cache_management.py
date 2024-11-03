import os
import sys
import unittest
import sqlite3
import json
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repo_map.cache_management import load_cache

class TestCacheManagement(unittest.TestCase):
    def setUp(self):
        # Use existing test_output directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_output')
        self.cache_file = os.path.join(self.test_dir, '.repo-map-cache.db')
        
        # Clean up any existing test database
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except PermissionError:
                pass  # File might be locked, will be overwritten

    def tearDown(self):
        # Ensure connections are closed
        if hasattr(self, 'cache_conn'):
            self.cache_conn.close()

    def test_load_cache_creates_new_db(self):
        # Test that load_cache creates a new database if it doesn't exist
        self.cache_conn = load_cache(self.test_dir)
        self.assertIsInstance(self.cache_conn, sqlite3.Connection)
        
        # Verify the cache file was created
        self.assertTrue(os.path.exists(self.cache_file))

        # Verify the table structure
        cursor = self.cache_conn.cursor()
        cursor.execute("PRAGMA table_info(cache)")
        columns = {info[1] for info in cursor.fetchall()}
        
        expected_columns = {
            'path',
            'hash',
            'description',
            'developer_consideration',
            'imports',
            'functions'
        }
        self.assertEqual(expected_columns, columns)

    def test_cache_operations(self):
        # Test basic cache operations
        self.cache_conn = load_cache(self.test_dir)
        cursor = self.cache_conn.cursor()

        # Use a unique path for this test
        test_data = {
            'path': '/test/cache_operations_test.py',
            'hash': 'abc123',
            'description': 'Test file',
            'developer_consideration': 'Test consideration',
            'imports': json.dumps(['os', 'sys']),
            'functions': json.dumps(['func1', 'func2'])
        }

        cursor.execute("""
            INSERT INTO cache (
                path, hash, description, developer_consideration, imports, functions
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_data['path'],
            test_data['hash'],
            test_data['description'],
            test_data['developer_consideration'],
            test_data['imports'],
            test_data['functions']
        ))
        self.cache_conn.commit()

        # Test retrieving data
        cursor.execute("SELECT * FROM cache WHERE path = ?", (test_data['path'],))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        
        # Verify the retrieved data
        self.assertEqual(row[0], test_data['path'])
        self.assertEqual(row[1], test_data['hash'])
        self.assertEqual(row[2], test_data['description'])
        self.assertEqual(row[3], test_data['developer_consideration'])
        self.assertEqual(json.loads(row[4]), json.loads(test_data['imports']))
        self.assertEqual(json.loads(row[5]), json.loads(test_data['functions']))

        # Test updating data
        new_description = "Updated test file"
        cursor.execute("""
            UPDATE cache
            SET description = ?
            WHERE path = ?
        """, (new_description, test_data['path']))
        self.cache_conn.commit()

        cursor.execute("SELECT description FROM cache WHERE path = ?", (test_data['path'],))
        updated_description = cursor.fetchone()[0]
        self.assertEqual(updated_description, new_description)

    def test_cache_persistence(self):
        # Test that cache persists between connections
        self.cache_conn = load_cache(self.test_dir)
        cursor = self.cache_conn.cursor()

        # Use a unique path for this test
        test_data = {
            'path': '/test/persistence_test.py',
            'hash': 'def456',
            'description': 'Persistence test',
            'developer_consideration': 'Test consideration',
            'imports': json.dumps(['os']),
            'functions': json.dumps(['test_func'])
        }

        cursor.execute("""
            INSERT INTO cache (
                path, hash, description, developer_consideration, imports, functions
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            test_data['path'],
            test_data['hash'],
            test_data['description'],
            test_data['developer_consideration'],
            test_data['imports'],
            test_data['functions']
        ))
        self.cache_conn.commit()
        self.cache_conn.close()

        # Open new connection and verify data persists
        self.cache_conn = load_cache(self.test_dir)
        cursor = self.cache_conn.cursor()
        
        cursor.execute("SELECT * FROM cache WHERE path = ?", (test_data['path'],))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], test_data['path'])
        self.assertEqual(row[1], test_data['hash'])

if __name__ == '__main__':
    unittest.main()
