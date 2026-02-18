"""Tests for Bedrock client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from src.bedrock_client import BedrockClient, BedrockError


class TestBedrockClient:
    """Test suite for BedrockClient."""
    
    def test_initialization_with_defaults(self):
        """Test client initialization with default values."""
        with patch('boto3.client') as mock_boto_client:
            client = BedrockClient()
            assert client.region_name == 'us-east-1'
            assert client.model_id == 'amazon.nova-lite-v1:0'
            mock_boto_client.assert_called_once()
    
    def test_initialization_with_custom_values(self):
        """Test client initialization with custom values."""
        with patch('boto3.client'):
            client = BedrockClient(
                region_name='us-west-2',
                model_id='amazon.nova-pro-v1:0'
            )
            assert client.region_name == 'us-west-2'
            assert client.model_id == 'amazon.nova-pro-v1:0'
    
    def test_invoke_model_success(self):
        """Test successful model invocation."""
        with patch('boto3.client') as mock_boto_client:
            # Setup mock response
            mock_response = {
                'body': MagicMock(),
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }
            response_body = {
                'output': {
                    'message': {
                        'content': [{'text': 'Generated summary text'}]
                    }
                }
            }
            mock_response['body'].read.return_value = json.dumps(response_body).encode()
            
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.return_value = mock_response
            mock_boto_client.return_value = mock_client_instance
            
            # Test invocation
            client = BedrockClient()
            result = client.invoke_model("Test prompt")
            
            assert result == 'Generated summary text'
            mock_client_instance.invoke_model.assert_called_once()
    
    def test_invoke_model_with_parameters(self):
        """Test model invocation with custom parameters."""
        with patch('boto3.client') as mock_boto_client:
            mock_response = {
                'body': MagicMock(),
            }
            response_body = {
                'output': {
                    'message': {
                        'content': [{'text': 'Response'}]
                    }
                }
            }
            mock_response['body'].read.return_value = json.dumps(response_body).encode()
            
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.return_value = mock_response
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient()
            result = client.invoke_model(
                "Test prompt",
                max_tokens=1024,
                temperature=0.5,
                top_p=0.8
            )
            
            # Verify the call was made with correct parameters
            call_args = mock_client_instance.invoke_model.call_args
            body = json.loads(call_args[1]['body'])
            
            assert body['inferenceConfig']['max_new_tokens'] == 1024
            assert body['inferenceConfig']['temperature'] == 0.5
            assert body['inferenceConfig']['top_p'] == 0.8
    
    def test_invoke_model_client_error(self):
        """Test handling of AWS ClientError."""
        with patch('boto3.client') as mock_boto_client:
            from botocore.exceptions import ClientError
            
            mock_client_instance = Mock()
            error_response = {
                'Error': {
                    'Code': 'AccessDeniedException',
                    'Message': 'Access denied'
                }
            }
            mock_client_instance.invoke_model.side_effect = ClientError(
                error_response, 'InvokeModel'
            )
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient()
            
            with pytest.raises(BedrockError) as exc_info:
                client.invoke_model("Test prompt")
            
            assert 'AccessDeniedException' in str(exc_info.value)
    
    def test_invoke_model_unexpected_response_format(self):
        """Test handling of unexpected response format."""
        with patch('boto3.client') as mock_boto_client:
            mock_response = {
                'body': MagicMock(),
            }
            # Invalid response format
            response_body = {'unexpected': 'format'}
            mock_response['body'].read.return_value = json.dumps(response_body).encode()
            
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.return_value = mock_response
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient()
            
            with pytest.raises(BedrockError) as exc_info:
                client.invoke_model("Test prompt")
            
            assert 'Unexpected response format' in str(exc_info.value)
