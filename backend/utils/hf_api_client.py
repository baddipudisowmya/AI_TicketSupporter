"""
Hugging Face OpenAI-Compatible API Client Utility.

This module centralizes all communication with the Hugging Face TGI Router endpoint,
which uses an OpenAI-compatible interface. It handles authentication, request formation,
and robust error handling, including timeouts and proxies.
"""
import os
import logging
import httpx
from openai import OpenAI, APIConnectionError

# --- Configuration ---
BASE_URL = "https://router.huggingface.co/v1"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

if not HF_API_TOKEN:
    raise ValueError("Hugging Face API token not found. Please set the HF_API_TOKEN environment variable.")

# --- Production-Grade Proxy Handling ---
http_proxy = os.getenv("HTTP_PROXY")
https_proxy = os.getenv("HTTPS_PROXY")
proxies = {"http://": http_proxy, "https://": https_proxy} if http_proxy or https_proxy else None
http_client = httpx.Client(proxy=proxies)

# --- Instantiate the OpenAI Client ---
client = OpenAI(
    base_url=BASE_URL,
    api_key=HF_API_TOKEN,
    http_client=http_client
)

# --- Models ---
# We will use a single powerful model for all tasks
LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

def query_chat_model(messages, model_name, is_json=False):
    """
    Sends a request to the specified chat model using the OpenAI-compatible API.

    Args:
        messages (list): A list of message dictionaries (e.g., [{"role": "user", "content": "..."}]).
        model_name (str): The name of the model to query.
        is_json (bool): If True, enables JSON mode for structured output.

    Returns:
        A tuple containing the response content (str) and an error (dict or None).
    """
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"} if is_json else None,
            timeout=30.0,
        )
        return completion.choices[0].message.content, None
    except APIConnectionError as err:
        logging.error(f"Request to Hugging Face API ({model_name}) failed: {err.__cause__}")
        error_message = f"An external API error occurred: {err.__class__.__name__}"
        return None, {"error": error_message}
    except Exception as err:
        logging.error(f"An unexpected error occurred when querying the model ({model_name}): {err}")
        return None, {"error": "An unexpected error occurred."}