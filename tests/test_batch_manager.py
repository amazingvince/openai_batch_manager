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