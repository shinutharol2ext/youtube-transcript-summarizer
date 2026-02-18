"""AWS Bedrock client for AI-powered summarization supporting all Bedrock models."""

import json
import os
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, BotoCoreError


# Supported Bedrock models with their request/response formats
BEDROCK_MODELS = {
    # Amazon Nova models
    'amazon.nova-micro-v1:0': 'nova',
    'amazon.nova-lite-v1:0': 'nova',
    'amazon.nova-pro-v1:0': 'nova',
    
    # Anthropic Claude models
    'anthropic.claude-3-5-sonnet-20241022-v2:0': 'claude',
    'anthropic.claude-3-5-haiku-20241022-v1:0': 'claude',
    'anthropic.claude-3-opus-20240229-v1:0': 'claude',
    'anthropic.claude-3-sonnet-20240229-v1:0': 'claude',
    'anthropic.claude-3-haiku-20240307-v1:0': 'claude',
    
    # Meta Llama models
    'meta.llama3-1-8b-instruct-v1:0': 'llama',
    'meta.llama3-1-70b-instruct-v1:0': 'llama',
    'meta.llama3-1-405b-instruct-v1:0': 'llama',
    'meta.llama3-2-1b-instruct-v1:0': 'llama',
    'meta.llama3-2-3b-instruct-v1:0': 'llama',
    'meta.llama3-2-11b-instruct-v1:0': 'llama',
    'meta.llama3-2-90b-instruct-v1:0': 'llama',
    
    # Mistral AI models
    'mistral.mistral-7b-instruct-v0:2': 'mistral',
    'mistral.mixtral-8x7b-instruct-v0:1': 'mistral',
    'mistral.mistral-large-2402-v1:0': 'mistral',
    'mistral.mistral-large-2407-v1:0': 'mistral',
    
    # AI21 Labs Jamba models
    'ai21.jamba-1-5-mini-v1:0': 'jamba',
    'ai21.jamba-1-5-large-v1:0': 'jamba',
    
    # Cohere Command models
    'cohere.command-r-v1:0': 'cohere',
    'cohere.command-r-plus-v1:0': 'cohere',
}


class BedrockClient:
    """Client for interacting with AWS Bedrock models."""
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        model_id: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None
    ):
        """
        Initialize Bedrock client.
        
        Args:
            region_name: AWS region (default: from env or us-east-1)
            model_id: Bedrock model ID (default: from env or amazon.nova-lite-v1:0)
            aws_access_key_id: AWS access key (optional, uses default credentials if not provided)
            aws_secret_access_key: AWS secret key (optional)
            aws_session_token: AWS session token (optional, for temporary credentials)
        """
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = model_id or os.getenv('BEDROCK_MODEL_ID', 'amazon.nova-lite-v1:0')
        
        # Determine model family
        self.model_family = self._get_model_family(self.model_id)
        
        # Build session kwargs
        session_kwargs = {}
        if aws_access_key_id:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
        if aws_secret_access_key:
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
        if aws_session_token:
            session_kwargs['aws_session_token'] = aws_session_token
        
        # Create boto3 session and client
        if session_kwargs:
            session = boto3.Session(**session_kwargs)
            self.client = session.client('bedrock-runtime', region_name=self.region_name)
        else:
            # Use default credentials (from ~/.aws/credentials or environment)
            self.client = boto3.client('bedrock-runtime', region_name=self.region_name)
    
    def _get_model_family(self, model_id: str) -> str:
        """
        Determine the model family from model ID.
        
        Args:
            model_id: Bedrock model ID
            
        Returns:
            Model family name
        """
        if model_id in BEDROCK_MODELS:
            return BEDROCK_MODELS[model_id]
        
        # Try to infer from model ID prefix
        if model_id.startswith('amazon.nova'):
            return 'nova'
        elif model_id.startswith('anthropic.claude'):
            return 'claude'
        elif model_id.startswith('meta.llama'):
            return 'llama'
        elif model_id.startswith('mistral.'):
            return 'mistral'
        elif model_id.startswith('ai21.jamba'):
            return 'jamba'
        elif model_id.startswith('cohere.command'):
            return 'cohere'
        else:
            # Default to nova format
            return 'nova'
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Invoke Bedrock model with a prompt.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text response
            
        Raises:
            BedrockError: If the API call fails
        """
        try:
            # Prepare request body based on model family
            request_body = self._prepare_request_body(prompt, max_tokens, temperature, top_p)
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response based on model family
            response_body = json.loads(response['body'].read())
            return self._parse_response(response_body)
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            raise BedrockError(f"Bedrock API error ({error_code}): {error_message}")
        except BotoCoreError as e:
            raise BedrockError(f"AWS connection error: {str(e)}")
        except Exception as e:
            raise BedrockError(f"Unexpected error calling Bedrock: {str(e)}")
    
    def _prepare_request_body(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> Dict[str, Any]:
        """Prepare request body based on model family."""
        
        if self.model_family == 'nova':
            # Amazon Nova format
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
            }
        
        elif self.model_family == 'claude':
            # Anthropic Claude format
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        
        elif self.model_family == 'llama':
            # Meta Llama format
            return {
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        
        elif self.model_family == 'mistral':
            # Mistral format
            return {
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        
        elif self.model_family == 'jamba':
            # AI21 Jamba format
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        
        elif self.model_family == 'cohere':
            # Cohere Command format
            return {
                "message": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "p": top_p
            }
        
        else:
            # Default to Nova format
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
            }
    
    def _parse_response(self, response_body: Dict[str, Any]) -> str:
        """Parse response based on model family."""
        
        if self.model_family == 'nova':
            # Amazon Nova response format
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message'].get('content', [])
                if content and len(content) > 0:
                    return content[0].get('text', '')
        
        elif self.model_family == 'claude':
            # Anthropic Claude response format
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0].get('text', '')
        
        elif self.model_family == 'llama':
            # Meta Llama response format
            if 'generation' in response_body:
                return response_body['generation']
        
        elif self.model_family == 'mistral':
            # Mistral response format
            if 'outputs' in response_body and len(response_body['outputs']) > 0:
                return response_body['outputs'][0].get('text', '')
        
        elif self.model_family == 'jamba':
            # AI21 Jamba response format
            if 'choices' in response_body and len(response_body['choices']) > 0:
                return response_body['choices'][0].get('message', {}).get('content', '')
        
        elif self.model_family == 'cohere':
            # Cohere Command response format
            if 'text' in response_body:
                return response_body['text']
        
        raise BedrockError(f"Unexpected response format from Bedrock model: {self.model_family}")


class BedrockError(Exception):
    """Exception raised for Bedrock API errors."""
    pass
