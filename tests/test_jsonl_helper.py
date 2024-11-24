import unittest
import os
import json
from openai_batch_manager.jsonl_helper import csv_to_jsonl, validate_jsonl, create_jsonl_manual

class TestJSONLHelper(unittest.TestCase):

    def setUp(self):
        # Setup temporary files
        self.csv_file = 'temp_test.csv'
        self.jsonl_file = 'temp_test.jsonl'
        with open(self.csv_file, 'w', encoding='utf-8') as f:
            f.write('name,age\n')
            f.write('Alice,30\n')
            f.write('Bob,25\n')

    def tearDown(self):
        # Remove temporary files
        for file in [self.csv_file, self.jsonl_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_csv_to_jsonl(self):
        csv_to_jsonl(self.csv_file, self.jsonl_file)
        with open(self.jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0]), {"name": "Alice", "age": "30"})
            self.assertEqual(json.loads(lines[1]), {"name": "Bob", "age": "25"})

    def test_validate_jsonl_valid(self):
        csv_to_jsonl(self.csv_file, self.jsonl_file)
        self.assertTrue(validate_jsonl(self.jsonl_file))

    def test_validate_jsonl_invalid(self):
        # Create an invalid JSONL file
        with open(self.jsonl_file, 'w', encoding='utf-8') as f:
            f.write('{"name": "Alice", "age": 30}\n')
            f.write('Invalid JSON Line\n')
        self.assertFalse(validate_jsonl(self.jsonl_file))

    def test_create_jsonl_manual(self):
        records = [{"name": "Charlie", "age": "22"}, {"name": "Dana", "age": "28"}]
        create_jsonl_manual(self.jsonl_file, records)
        with open(self.jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0]), {"name": "Charlie", "age": "22"})
            self.assertEqual(json.loads(lines[1]), {"name": "Dana", "age": "28"})

if __name__ == '__main__':
    unittest.main()