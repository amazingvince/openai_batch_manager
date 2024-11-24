Absolutely! Enhancing your **OpenAI Batch Manager** package with functionality to create and manage JSONL files will make it even more versatile and user-friendly. Below, I'll guide you through adding a new module and corresponding CLI commands to help users generate JSONL files from various sources, such as CSV files or manual input.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Implementing JSONL Helper Module](#implementing-jsonl-helper-module)
4. [Updating the CLI](#updating-the-cli)
5. [Updating `setup.py`](#updating-setuppy)
6. [Adding Documentation](#adding-documentation)
7. [Complete Code Example](#complete-code-example)
8. [Usage Instructions](#usage-instructions)
9. [Testing the New Feature](#testing-the-new-feature)

---

## Overview

We'll add a **JSONL Helper** module to your existing package that allows users to:

- **Convert CSV to JSONL**: Easily transform CSV files into JSONL format.
- **Validate JSONL Files**: Ensure that JSONL files are correctly formatted.
- **Create JSONL from Manual Input**: Allow users to input JSON objects manually to create a JSONL file.

To achieve this, we'll:

1. **Create a new module**: `jsonl_helper.py` containing necessary functions.
2. **Update the CLI**: Add new subcommands for JSONL operations.
3. **Ensure proper packaging**: Update `setup.py` and other necessary files.
4. **Provide usage instructions**: Update `README.md` accordingly.

---

## Project Structure

After adding the JSONL helper, your project structure will look like this:

```
openai_batch_manager/
├── openai_batch_manager/
│   ├── __init__.py
│   ├── batch_manager.py
│   ├── cli.py
│   ├── config.py
│   ├── utils.py
│   └── jsonl_helper.py        # New module
├── tests/
│   └── test_batch_manager.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
└── MANIFEST.in
```

---

## Implementing JSONL Helper Module

Create a new file named `jsonl_helper.py` inside the `openai_batch_manager` package. This module will contain functions to:

1. **Convert CSV to JSONL**
2. **Validate JSONL Files**
3. **Create JSONL from Manual Input**

### `openai_batch_manager/jsonl_helper.py`

```python
# openai_batch_manager/jsonl_helper.py

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
```

### Explanation

- **Logging**: Configured to log both to the console and a file named `jsonl_helper.log`.
- **`csv_to_jsonl`**: Converts a CSV file to JSONL by reading each row as a dictionary and writing it as a JSON object per line.
- **`validate_jsonl`**: Checks each line in a JSONL file to ensure it contains valid JSON.
- **`create_jsonl_manual`**: Allows creating a JSONL file from a list of JSON objects provided programmatically.

---

## Updating the CLI

We'll integrate the new JSONL helper functionalities into the existing CLI by adding subcommands. We'll use `click`'s group feature to manage multiple commands.

### Update `cli.py`

Modify `openai_batch_manager/cli.py` to include a new group for JSONL operations.

```python
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
```

### Explanation

- **`@click.group()`**: Creates a CLI group named `cli` to manage multiple subcommands.
- **`@cli.command()`**: Defines the `process` command for batch processing.
- **`@cli.group()`**: Creates a subgroup named `jsonl` for JSONL operations.
- **`@jsonl.command()`**: Adds subcommands under the `jsonl` group:
  - **`csv-to-jsonl`**: Converts a CSV file to JSONL.
  - **`validate`**: Validates a JSONL file.
  - **`create-manual`**: Creates a JSONL file from manual JSON key-value pairs.

This structure allows users to perform both batch processing and JSONL operations using a single CLI tool with organized commands.

---

## Updating `setup.py`

Ensure that the new `jsonl_helper.py` is included in the package and that the CLI recognizes all new commands.

### No Changes Needed in `setup.py`

Since we've added `jsonl_helper.py` within the existing package, and updated the `cli.py` with new commands, no changes are needed in `setup.py`. However, ensure that `include_package_data=True` is set to include all necessary files.

```python
# setup.py remains the same as previously provided
```

---

## Adding Documentation

Update your `README.md` to include instructions for the new JSONL functionalities.

### Update `README.md`

````markdown
# OpenAI Batch Manager

A command-line tool to manage OpenAI batch processing for large JSONL files. It splits the input file into manageable chunks, uploads each chunk as a batch job, polls for completion, downloads the results, and cleans up temporary files. Additionally, it provides utilities to create and validate JSONL files.

## Features

- **Splitting Large JSONL Files**: Breaks down large input files into smaller chunks.
- **Batch Processing**: Uploads each chunk as a separate batch job to OpenAI's API.
- **Polling & Progress Tracking**: Monitors the status of each batch with real-time progress bars.
- **Result Downloading**: Retrieves and saves the results of completed batches.
- **Automatic Clean-Up**: Deletes temporary chunk files after successful processing.
- **Retries & Error Handling**: Implements retries with exponential backoff for robustness.
- **Logging**: Logs detailed information to both the console and a log file.
- **JSONL Utilities**:
  - **Convert CSV to JSONL**: Easily transform CSV files into JSONL format.
  - **Validate JSONL Files**: Ensure that JSONL files are correctly formatted.
  - **Create JSONL from Manual Input**: Allow users to input JSON objects manually to create a JSONL file.

## Installation

### Prerequisites

- **Python 3.7+**

### Install via `pip`

```bash
pip install openai-batch-manager
```
````

Alternatively, install from source:

```bash
git clone https://github.com/yourusername/openai_batch_manager.git
cd openai_batch_manager
pip install .
```

## Configuration

The tool uses environment variables for configuration. Create a `.env` file in your home directory or project directory with the following content:

```dotenv
# .env

API_KEY=your_openai_api_key_here
COMPLETION_WINDOW=24h
ENDPOINT=/v1/completions
```

**Security Tip:** Ensure `.env` is excluded from version control to protect sensitive information.

## Usage

### Batch Processing

Process a JSONL file by splitting it into chunks, uploading batches, polling for completion, downloading results, and cleaning up.

```bash
openai-batch-manager process --input /path/to/input.jsonl --output /path/to/output/
```

#### Options

- `--input`, `-i`: **(Required)** Path to the input JSONL file.
- `--output`, `-o`: **(Required)** Directory to save the results.
- `--chunk-size`, `-c`: Number of lines per chunk (default: 1000).
- `--completion-window`: Completion window for batch processing (default: `24h`).
- `--endpoint`: API endpoint to use for batch processing (default: `/v1/completions`).

#### Example

```bash
openai-batch-manager process -i data/input.jsonl -o data/results/ -c 500 --completion-window 24h --endpoint /v1/chat/completions
```

### JSONL File Operations

#### Convert CSV to JSONL

Convert a CSV file to JSONL format.

```bash
openai-batch-manager jsonl csv-to-jsonl --csv-file /path/to/input.csv --jsonl-file /path/to/output.jsonl
```

#### Options

- `--csv-file`, `-c`: **(Required)** Path to the input CSV file.
- `--jsonl-file`, `-j`: **(Required)** Path to the output JSONL file.

#### Example

```bash
openai-batch-manager jsonl csv-to-jsonl -c data/input.csv -j data/output.jsonl
```

#### Validate JSONL File

Check if a JSONL file is correctly formatted.

```bash
openai-batch-manager jsonl validate --jsonl-file /path/to/file.jsonl
```

#### Options

- `--jsonl-file`, `-j`: **(Required)** Path to the JSONL file to validate.

#### Example

```bash
openai-batch-manager jsonl validate -j data/output.jsonl
```

#### Create JSONL from Manual Input

Create a JSONL file by manually specifying JSON key-value pairs.

```bash
openai-batch-manager jsonl create-manual --jsonl-file /path/to/output.jsonl --record key1 value1 --record key2 value2
```

#### Options

- `--jsonl-file`, `-j`: **(Required)** Path to the output JSONL file.
- `--record`, `-r`: JSON key-value pair. Can be used multiple times.

#### Example

```bash
openai-batch-manager jsonl create-manual -j data/manual_output.jsonl -r name Alice -r age 30
```

This command creates a JSONL file `manual_output.jsonl` with the following content:

```json
{ "name": "Alice", "age": "30" }
```

## Logging

Logs are saved to `batch_manager.log` and `jsonl_helper.log` in the current directory. Detailed logs include information about uploads, batch creation, status polling, downloads, and errors.

## Development

### Setting Up the Development Environment

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/openai_batch_manager.git
   cd openai_batch_manager
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install the Package in Editable Mode:**

   ```bash
   pip install -e .
   ```

### Running Tests

_Implement your tests in the `tests/` directory and run them using your preferred test runner (e.g., `pytest`)._

## Contributing

Contributions are welcome! Please open issues and submit pull requests for any enhancements or bug fixes.

## License

[MIT License](LICENSE)

````

---

## Complete Code Example

Below is the complete codebase with the new JSONL helper feature integrated.

### `.env`

```dotenv
# .env

API_KEY=your_openai_api_key_here
COMPLETION_WINDOW=24h
ENDPOINT=/v1/completions
````

### `setup.py`

```python
# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openai-batch-manager",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to manage OpenAI batch processing for large JSONL files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/openai_batch_manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "httpx",
        "asyncio",
        "tqdm",
        "python-dotenv",
        "tenacity",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "openai-batch-manager=openai_batch_manager.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
```

### `MANIFEST.in`

```text
# MANIFEST.in

include README.md
include LICENSE
include .env
```

### `requirements.txt`

```text
httpx
asyncio
tqdm
python-dotenv
tenacity
click
```

### `openai_batch_manager/__init__.py`

```python
# openai_batch_manager/__init__.py

# This file can be empty or include package-level imports
```

### `openai_batch_manager/config.py`

```python
# openai_batch_manager/config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
COMPLETION_WINDOW = os.getenv("COMPLETION_WINDOW", "24h")
ENDPOINT = os.getenv("ENDPOINT", "/v1/completions")

# Validate essential configurations
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")
```

### `openai_batch_manager/utils.py`

```python
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
```

### `openai_batch_manager/jsonl_helper.py`

```python
# openai_batch_manager/jsonl_helper.py

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
```

### `openai_batch_manager/batch_manager.py`

```python
# openai_batch_manager/batch_manager.py

import asyncio
import httpx
import json
import time
from typing import List, Optional, Dict
from openai_batch_manager.config import (
    API_KEY,
    COMPLETION_WINDOW,
    ENDPOINT,
)
from openai_batch_manager.utils import ensure_directory, clean_up_files
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from tqdm.asyncio import tqdm_asyncio

# Configure logger
logger = logging.getLogger("BatchManager")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
fh = logging.FileHandler("batch_manager.log")
fh.setFormatter(formatter)
logger.addHandler(fh)


class BatchManager:
    def __init__(self, api_key: str, endpoint: str, completion_window: str, output_dir: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.completion_window = completion_window
        self.output_dir = output_dir
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,  # Adjust as needed
        )

    async def close(self):
        await self.client.aclose()

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def upload_file(self, file_path: str) -> str:
        """
        Uploads a JSONL file to OpenAI and returns the file ID.
        Retries on network-related errors.
        """
        logger.info(f"Uploading file: {file_path}")
        upload_url = "/v1/files"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/jsonl')}
            data = {'purpose': 'batch'}
            try:
                response = await self.client.post(upload_url, files=files, data=data)
                response.raise_for_status()
                file_id = response.json()['id']
                logger.info(f"Uploaded file ID: {file_id}")
                return file_id
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during file upload: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during file upload: {e}")
                raise

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def create_batch(self, input_file_id: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Creates a batch job and returns the batch ID.
        Retries on network-related errors.
        """
        logger.info(f"Creating batch job for file ID: {input_file_id}")
        create_url = "/v1/batches"
        payload = {
            "completion_window": self.completion_window,
            "endpoint": self.endpoint,
            "input_file_id": input_file_id,
        }
        if metadata:
            payload["metadata"] = metadata
        try:
            response = await self.client.post(create_url, json=payload)
            response.raise_for_status()
            batch_id = response.json()['id']
            logger.info(f"Created batch ID: {batch_id}")
            return batch_id
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during batch creation: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during batch creation: {e}")
            raise

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def get_batch_status(self, batch_id: str) -> dict:
        """
        Retrieves the status of a batch.
        Retries on network-related errors.
        """
        logger.debug(f"Checking status for batch ID: {batch_id}")
        retrieve_url = f"/v1/batches/{batch_id}"
        try:
            response = await self.client.get(retrieve_url)
            response.raise_for_status()
            status_info = response.json()
            logger.debug(f"Batch {batch_id} status: {status_info.get('status')}")
            return status_info
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during status retrieval: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during status retrieval: {e}")
            raise

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
    )
    async def download_batch_results(self, batch_id: str, output_file: str):
        """
        Downloads the results of a completed batch.
        Retries on network-related errors.
        """
        logger.info(f"Downloading results for batch ID: {batch_id} to {output_file}")
        # Assuming the API provides a URL to download the results
        # Adjust based on actual API response
        batch_info = await self.get_batch_status(batch_id)
        download_url = batch_info.get('output_file_url')
        if not download_url:
            logger.error(f"Output file URL not found for batch ID: {batch_id}")
            raise ValueError("Output file URL not found in batch info.")
        try:
            response = await self.client.get(download_url)
            response.raise_for_status()
            with open(output_file, 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded results to {output_file}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during result download: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during result download: {e}")
            raise

    async def process_batch(self, chunk_file: str):
        """
        Handles the entire lifecycle of a single batch.
        """
        try:
            file_id = await self.upload_file(chunk_file)
            batch_id = await self.create_batch(file_id)

            # Polling for batch completion with progress tracking
            status = None
            with tqdm_asyncio(total=100, desc=f"Batch {batch_id}", unit="%", leave=True) as pbar:
                while True:
                    status_info = await self.get_batch_status(batch_id)
                    status = status_info.get('status')
                    if status == 'succeeded':
                        pbar.update(100 - pbar.n)  # Complete the progress bar
                        break
                    elif status in ['failed', 'cancelled']:
                        pbar.write(f"Batch {batch_id} ended with status: {status}")
                        raise RuntimeError(f"Batch {batch_id} ended with status: {status}")
                    else:
                        # Update progress bar based on some logic or keep it indeterminate
                        pbar.update(10)  # Example: increment progress
                        await asyncio.sleep(30)  # Wait before next poll

            # Download results if succeeded
            if status == 'succeeded':
                output_file = f"{self.output_dir}/results_{batch_id}.jsonl"
                await self.download_batch_results(batch_id, output_file)
        except Exception as e:
            logger.error(f"Error processing batch for file {chunk_file}: {e}")
            raise

    async def process_batches(self, chunk_files: List[str]):
        """
        Processes multiple batches sequentially with progress tracking and clean-up.
        """
        ensure_directory(self.output_dir)
        failed_batches = []
        processed_files = []

        for chunk_file in tqdm_asyncio(chunk_files, desc="Processing Batches", unit="batch"):
            try:
                await self.process_batch(chunk_file)
                processed_files.append(chunk_file)
            except Exception as e:
                logger.error(f"Failed to process batch for file {chunk_file}: {e}")
                failed_batches.append(chunk_file)

        # Clean up successfully processed chunk files
        clean_up_files(processed_files, logger)

        if failed_batches:
            logger.warning(f"The following batches failed to process: {failed_batches}")
        else:
            logger.info("All batches processed successfully.")
```

### `openai_batch_manager/cli.py`

```python
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
    click.echo(f"Converted '{csv_file}' to '{jsonl_file}' successfully.")


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
```

### `openai_batch_manager/jsonl_helper.py`

_(As provided above)_

### `README.md`

_(As provided above)_

### `LICENSE`

_(As provided above)_

### `tests/test_batch_manager.py`

```python
# tests/test_batch_manager.py

import unittest
from unittest.mock import patch, AsyncMock
from openai_batch_manager.batch_manager import BatchManager

class TestBatchManager(unittest.IsolatedAsyncioTestCase):

    @patch('openai_batch_manager.batch_manager.httpx.AsyncClient')
    async def test_upload_file_success(self, mock_client):
        # Setup
        mock_response = AsyncMock()
        mock_response.json.return_value = {'id': 'file_123'}
        mock_response.raise_for_status = AsyncMock()
        mock_client.return_value.post.return_value = mock_response

        manager = BatchManager(api_key='test_key', endpoint='/v1/completions', completion_window='24h', output_dir='.')

        # Execute
        file_id = await manager.upload_file('test.jsonl')

        # Assert
        self.assertEqual(file_id, 'file_123')
        mock_client.return_value.post.assert_called_once()

    # Add more tests for other methods

if __name__ == '__main__':
    unittest.main()
```

### `tests/test_jsonl_helper.py`

_(Optionally, create tests for JSONL helper)_

```python
# tests/test_jsonl_helper.py

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
```

---

## Usage Instructions

After completing the above steps, you can use your **OpenAI Batch Manager** with JSONL helper functionalities as follows:

### 1. Install the Package

If you haven't already installed the package, do so now:

```bash
pip install .
```

Or, if you made changes and want to install in editable mode:

```bash
pip install -e .
```

### 2. Configure Environment Variables

Ensure your `.env` file is correctly set up with your OpenAI API key and other configurations.

```dotenv
# .env

API_KEY=your_openai_api_key_here
COMPLETION_WINDOW=24h
ENDPOINT=/v1/completions
```

### 3. Using the CLI

#### a. Batch Processing

Process a JSONL file:

```bash
openai-batch-manager process --input path/to/input.jsonl --output path/to/output/
```

#### b. JSONL File Operations

##### Convert CSV to JSONL

```bash
openai-batch-manager jsonl csv-to-jsonl --csv-file path/to/input.csv --jsonl-file path/to/output.jsonl
```

##### Validate JSONL File

```bash
openai-batch-manager jsonl validate --jsonl-file path/to/file.jsonl
```

##### Create JSONL from Manual Input

```bash
openai-batch-manager jsonl create-manual --jsonl-file path/to/output.jsonl --record name Alice --record age 30
```

This command creates a JSONL file `output.jsonl` with the following content:

```json
{ "name": "Alice", "age": "30" }
```

You can add multiple `--record` options to include more records.

---

## Testing the New Feature

Ensure all functionalities work as expected by running the provided unit tests.

### Running Tests

```bash
python -m unittest discover tests
```

This command discovers and runs all tests in the `tests/` directory.

---

## Additional Enhancements

Here are some suggestions to further improve your package:

1. **Enhanced CLI Options**: Allow more flexibility in JSONL creation, such as specifying delimiter for CSV, handling nested JSON objects, etc.
2. **Concurrency**: Implement concurrent processing of batches to improve performance while respecting API rate limits.
3. **Error Notifications**: Integrate email or messaging notifications for batch failures.
4. **Dockerization**: Containerize the application for consistent environments across different systems.
5. **Advanced Logging**: Implement log rotation to manage log file sizes.
6. **Interactive Mode**: Allow users to input JSON objects interactively for JSONL creation.

---

By following this guide, you've successfully extended your **OpenAI Batch Manager** package to include robust JSONL creation and management functionalities, all accessible through a user-friendly CLI. This makes your tool more comprehensive and easier to use for various data preparation and batch processing tasks.

Feel free to further customize and enhance the package to better fit your specific needs!
