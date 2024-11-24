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

```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please open issues and submit pull requests for any enhancements or bug fixes.

## License

[MIT License](LICENSE)
