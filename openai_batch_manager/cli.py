# openai_batch_manager/cli.py

import asyncio
import click
import logging
from openai_batch_manager.batch_manager import BatchManager
from openai_batch_manager.utils import split_jsonl_file, ensure_directory, clean_up_files
from openai_batch_manager.jsonl_helper import csv_to_jsonl, validate_jsonl, create_jsonl_manual
from openai_batch_manager.config import (
    API_KEY,
    COMPLETION_WINDOW,
    ENDPOINT,
)
from tqdm.asyncio import tqdm_asyncio

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


@click.group()
def cli():
    """
    OpenAI Batch Manager CLI

    Manage batch processing and JSONL file operations with OpenAI's API.
    """
    pass


@cli.command()
@click.option(
    '--input',
    '-i',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help='Path to the input JSONL file.'
)
@click.option(
    '--output',
    '-o',
    required=True,
    type=click.Path(file_okay=False),
    help='Directory to save the results.'
)
@click.option(
    '--chunk-size',
    '-c',
    default=1000,
    show_default=True,
    type=int,
    help='Number of lines per chunk.'
)
@click.option(
    '--completion-window',
    default='24h',
    show_default=True,
    type=str,
    help='Completion window for batch processing.'
)
@click.option(
    '--endpoint',
    default='/v1/completions',
    show_default=True,
    type=str,
    help='API endpoint to use for batch processing.'
)
def process(input, output, chunk_size, completion_window, endpoint):
    """
    Process a JSONL file by splitting it into chunks, uploading batches,
    polling for completion, downloading results, and cleaning up.
    """
    asyncio.run(run_batch_processing(input, output, chunk_size, completion_window, endpoint))


@cli.group()
def jsonl():
    """
    JSONL File Operations

    Create, convert, and validate JSONL files.
    """
    pass


@jsonl.command('csv-to-jsonl')
@click.option(
    '--csv-file',
    '-c',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help='Path to the input CSV file.'
)
@click.option(
    '--jsonl-file',
    '-j',
    required=True,
    type=click.Path(dir_okay=False),
    help='Path to the output JSONL file.'
)
def csv_to_jsonl_command(csv_file, jsonl_file):
    """
    Convert a CSV file to a JSONL file.
    """
    csv_to_jsonl(csv_file, jsonl_file)


@jsonl.command('validate')
@click.option(
    '--jsonl-file',
    '-j',
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help='Path to the JSONL file to validate.'
)
def validate_jsonl_command(jsonl_file):
    """
    Validate the format of a JSONL file.
    """
    is_valid = validate_jsonl(jsonl_file)
    if is_valid:
        click.echo(f"JSONL file '{jsonl_file}' is valid.")
    else:
        click.echo(f"JSONL file '{jsonl_file}' is invalid.", err=True)


@jsonl.command('create-manual')
@click.option(
    '--jsonl-file',
    '-j',
    required=True,
    type=click.Path(dir_okay=False),
    help='Path to the output JSONL file.'
)
@click.option(
    '--record',
    '-r',
    multiple=True,
    type=(str, str),
    help='JSON key-value pair. Can be used multiple times.'
)
def create_jsonl_manual_command(jsonl_file, record):
    """
    Create a JSONL file from manual JSON key-value pairs.
    Example:
        --record key1 value1 --record key2 value2
    """
    records = []
    current_record = {}
    for key, value in record:
        current_record[key] = value
    if current_record:
        records.append(current_record)
    create_jsonl_manual(jsonl_file, records)
    click.echo(f"JSONL file '{jsonl_file}' created with {len(records)} records.")


async def run_batch_processing(input_file, output_dir, chunk_size, completion_window, endpoint):
    from openai_batch_manager.batch_manager import BatchManager  # Import inside function to avoid circular imports

    # Initialize BatchManager
    manager = BatchManager(
        api_key=API_KEY,
        endpoint=endpoint,
        completion_window=completion_window,
        output_dir=output_dir
    )

    try:
        # Split the large JSONL file into chunks
        logging.info("Splitting the input JSONL file into chunks...")
        chunk_files = split_jsonl_file(input_file, chunk_size)
        logging.info(f"Total chunks created: {len(chunk_files)}")

        if not chunk_files:
            logging.warning("No chunks were created. Please check the input file and chunk size.")
            return

        # Process each batch sequentially with progress tracking
        await manager.process_batches(chunk_files)
    except Exception as e:
        logging.error(f"An error occurred during batch processing: {e}")
    finally:
        await manager.close()


if __name__ == "__main__":
    cli()
