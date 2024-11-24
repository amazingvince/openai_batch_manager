# openai_batch_manager/utils.py

import os
from typing import List
import logging

def split_jsonl_file(input_file: str, chunk_size: int) -> List[str]:
    """
    Splits a large JSONL file into smaller chunks.

    Args:
        input_file (str): Path to the input JSONL file.
        chunk_size (int): Number of lines per chunk.

    Returns:
        List[str]: List of file paths for the created chunks.
    """
    chunk_files = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        chunk = []
        chunk_index = 1
        for line_number, line in enumerate(infile, start=1):
            chunk.append(line)
            if line_number % chunk_size == 0:
                chunk_filename = f"{input_file}_chunk_{chunk_index}.jsonl"
                with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
                    chunk_file.writelines(chunk)
                chunk_files.append(chunk_filename)
                chunk = []
                chunk_index += 1
        # Write remaining lines
        if chunk:
            chunk_filename = f"{input_file}_chunk_{chunk_index}.jsonl"
            with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
                chunk_file.writelines(chunk)
            chunk_files.append(chunk_filename)
    return chunk_files

def ensure_directory(path: str):
    """
    Ensures that the specified directory exists.

    Args:
        path (str): Directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def clean_up_files(file_paths: List[str], logger: logging.Logger):
    """
    Deletes the specified files.

    Args:
        file_paths (List[str]): List of file paths to delete.
        logger (logging.Logger): Logger for logging the actions.
    """
    for file_path in file_paths:
        try:
            os.remove(file_path)
            logger.info(f"Deleted temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
