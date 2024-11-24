import csv
import json
import os
from typing import List, Dict
import logging

logger = logging.getLogger("JSONLHelper")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
fh = logging.FileHandler("jsonl_helper.log")
fh.setFormatter(formatter)
logger.addHandler(fh)


def csv_to_jsonl(csv_file: str, jsonl_file: str):
    """
    Converts a CSV file to a JSONL file.

    Args:
        csv_file (str): Path to the input CSV file.
        jsonl_file (str): Path to the output JSONL file.
    """
    logger.info(f"Converting CSV '{csv_file}' to JSONL '{jsonl_file}'")
    try:
        with open(csv_file, 'r', encoding='utf-8') as f_csv, open(jsonl_file, 'w', encoding='utf-8') as f_jsonl:
            reader = csv.DictReader(f_csv)
            for row in reader:
                json_line = json.dumps(row)
                f_jsonl.write(json_line + '\n')
        logger.info(f"Successfully converted '{csv_file}' to '{jsonl_file}'")
    except Exception as e:
        logger.error(f"Error converting CSV to JSONL: {e}")
        raise


def validate_jsonl(jsonl_file: str) -> bool:
    """
    Validates the format of a JSONL file.

    Args:
        jsonl_file (str): Path to the JSONL file.

    Returns:
        bool: True if valid, False otherwise.
    """
    logger.info(f"Validating JSONL file '{jsonl_file}'")
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON at line {line_number}: {e}")
                    return False
        logger.info(f"JSONL file '{jsonl_file}' is valid")
        return True
    except Exception as e:
        logger.error(f"Error validating JSONL file: {e}")
        raise


def create_jsonl_manual(jsonl_file: str, records: List[Dict]):
    """
    Creates a JSONL file from a list of JSON objects.

    Args:
        jsonl_file (str): Path to the output JSONL file.
        records (List[Dict]): List of JSON objects.
    """
    logger.info(f"Creating JSONL file '{jsonl_file}' from manual input")
    try:
        with open(jsonl_file, 'w', encoding='utf-8') as f_jsonl:
            for record in records:
                json_line = json.dumps(record)
                f_jsonl.write(json_line + '\n')
        logger.info(f"Successfully created JSONL file '{jsonl_file}'")
    except Exception as e:
        logger.error(f"Error creating JSONL file: {e}")
        raise
