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
