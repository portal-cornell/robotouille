"""
This module acts as a wrapper for LLMs including
- OpenAI GPTs
- Google Gemini
- Anthropic Claude
- HuggingFace's transformers pipeline for Open LLMs
"""
import os
import time

import openai
from openai.types.chat.chat_completion import ChatCompletion
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODELS = []

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

import anthropic # API key automatically retrieved from ANTHROPIC_API_KEY
ANTHROPIC_MODELS = [
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

from gpt_cost_estimator import CostEstimator

import transformers
import torch

import logging
logger = logging.getLogger(__name__)

LOADED_PIPELINES = {}

def get_openai_llms():
    """Returns the available OpenAI LLMs compatible with the Chat API.

    Returns:
        openai_llm_names (List[str])
            The available OpenAI LLMs compatible with the Chat API.
    """
    global OPENAI_MODELS
    if len(OPENAI_MODELS) == 0:
        client = openai.OpenAI()
        openai_models = client.models.list()
        OPENAI_MODELS = [model.id for model in openai_models]
    return OPENAI_MODELS

def convert_to_google_message(messages):
    """Converts the messages to the Google format.

    Parameters:
        messages (List[Dict[str, str]])
            The messages to convert to the Google format.
    
    Returns:
        google_messages (List[Dict[str, str]])
            The messages in the Google format.
    """
    system_msg = messages[0]
    google_messages = [
        {
            "role": "user", 
            "parts": f"{system_msg['content']}\n{messages[1]['content']}"
        }
    ]
    for message in messages[2:]:
        role = "model" if message["role"] == "assistant" else "user"
        google_messages.append({"role": role, "parts": message["content"]})
    return google_messages

def convert_to_alternating_role_messages(messages):
    """Converts the messages to alternating role messages.

    Enforces that messages are in alternating user-assistant roles. This is
    used for Anthropic's chat API and open-source LLMs like LLama2.

    Parameters:
        messages (List[Dict[str, str]])
            The messages to convert to alternating role messages.
    
    Returns:
        alternating_role_messages (List[Dict[str, str]])
            The messages in alternating role messages.
    """
    new_messages = [messages[0]]
    last_role = messages[0]["role"]
    for message in messages[1:]:
        if last_role == message["role"]:
            new_messages[-1]["content"] += f"\n{message['content']}"
        else:
            new_messages.append(message)
        last_role = message["role"]
    return new_messages

@CostEstimator()
def call_openai_chat(messages=[], model="gpt-3.5-turbo", temperature=0.0, max_attempts=10, sleep_time=5, **kwargs):
    """Sends chat messages to OpenAI's chat API and returns a response if successful.

    This function will raise BadRequestError if the request to the OpenAI API is invalid to handle
    the error in the policy.

    Parameters:
        messages (list)
            A list of dictionaries containing the messages to query the LLM with
        model (str)
            The LLM model to use. Default is "gpt-3.5-turbo"
        temperature (float)
            The LLM temperature to use. Defaults to 0. Note that a temperature of 0 does not 
            guarantee the same response (https://community.openai.com/t/why-the-api-output-is-inconsistent-even-after-the-temperature-is-set-to-0/329541/9).
        max_attempts (int)
            The number of attempts to query the LLM before giving up
        sleep_time (int)
            The number of seconds to sleep after a failed query before requerying

    Returns:
        response (Optional[dict])
            The response from OpenAI's chat API, if any.
    
    Raises:
        AssertionError
            If the OpenAI API key is invalid
        openai.BadRequestError
            If the request to the OpenAI API is invalid
    """
    client = openai.OpenAI()

    num_attempts = 0
    response = None
    while response is None and num_attempts < max_attempts:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
        except openai.BadRequestError as e:
            raise e # Reraise the error for the policy to handle
        except openai.OpenAIError as e:
            assert not isinstance(e, openai.AuthenticationError), "Invalid OpenAI API key"
            print(e)
            print(f"API Error #{num_attempts+1}: Sleeping...")
            time.sleep(sleep_time)
            num_attempts += 1
    return response

def combine_successive_role_messages(messages):
    """Combines successive role messages into a single message.

    LLM models like Llama-2 only allow user/assistant/user/assistant/... message order. This
    function formats the messages to comply with this requirement.

    Parameters:
        messages (List[Dict[str, str]])
            The messages to combine.

    Returns:
        new_messages (List[Dict[str, str]])
            The messages with successive role messages combined.
    """
    new_messages = [messages[0]]
    last_role = None
    for message in messages[1:]:
        if last_role == message["role"]:
            new_messages[-1]["content"] += f"\n{message['content']}"
        else:
            new_messages.append(message)
        last_role = message["role"]
    return new_messages

def reset_accumulated_cost():
    """Resets the accumulated cost of the OpenAI API calls.
    
    Side Effects:
        - The accumulated cost of the OpenAI API calls is reset.
    """
    CostEstimator.reset()

def get_accumulated_cost():
    """Returns the accumulated cost of the OpenAI API calls.

    Returns:
        accumulated_cost (float)
            The accumulated cost of the OpenAI API calls.
    """
    return CostEstimator().get_total_cost()

def prompt_llm(user_prompt, messages, model, temperature, history=[], **kwargs):
    """Prompt an LLM with the given prompt and return the response.

    Parameters:
        user_prompt (str)
            The user prompt to parse.
        messages (List[Dict[str, str]])
            The messages to query the LLM with.
        model (str)
            The LLM model to use.
        temperature (float)
            The LLM temperature to use.
        history (List[Dict[str, str]])
            The history of alternating user-assistant messages to query the LLM with.
        kwargs (Dict[str, any])
            Optional parameters for LLM querying such as:
                max_attempts (int)
                    The number of attempts to query the LLM before giving up
                sleep_time (int)
                    The number of seconds to sleep after a failed query before requerying
                debug (bool)
                    Whether or not to mock an LLM response
                mock (bool)
                    Whether or not to send a mock respones with gpt_cost_estimator
                completion_tokens (int)
                    The number of completion tokens to mock query the LLM with.

    Returns:
        response (Optional[dict])
            The response from OpenAI's chat API, if any.
    
    Raises:
        AssertionError
            If the prompt YAML is invalid.
        NotImplementedError
            - If the prompt parsing version is not supported.
            - If the data tag is not implemented.
    """
    debug = kwargs.get('debug', False)
    if debug:
        response = input("Please input the mocked LLM response: ")
    elif model in get_openai_llms():
        messages = messages.copy()
        if history:
            assert len(history) % 2 == 0, "History must have an even number of messages"
            for i, message in enumerate(history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": message})
        messages.append({"role": "user", "content": user_prompt})
        response = call_openai_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            **kwargs
        )
        logger.info(f"LLM Accumulated Cost: ${get_accumulated_cost()}")
        if isinstance(response, ChatCompletion):
            prompt_tokens = response.usage.prompt_tokens
            logger.info(f"Prompt Tokens: {prompt_tokens}")
            completion_tokens = response.usage.completion_tokens
            logger.info(f"Completion Tokens: {completion_tokens}")
            response = response.choices[0].message.content
        elif isinstance(response, dict):
            # Mocked response
            response = response['choices'][0]['message']['content']
    elif f"models/{model}" in [m.name for m in genai.list_models()]:
        google_model = genai.GenerativeModel(model)
        google_messages = convert_to_google_message(messages)
        chat = google_model.start_chat(history=google_messages)
        response = chat.send_message(user_prompt)
        response = response.text
    elif model in ANTHROPIC_MODELS:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        system_msg = messages[0]["content"]
        anthropic_messages = convert_to_alternating_role_messages(messages[1:])
        anthropic_messages.append({"role": "user", "content": user_prompt})
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_msg,
            messages=anthropic_messages
        )
        response = response.content[0].text
    else:
        # Open LLM
        client = openai.Client(base_url="http://127.0.0.1:30000/v1", api_key="None") # SGLang
        
        if "Llama-2" in model or "Llama-3.1" in model:
            # Alternating conversation roles
            messages = combine_successive_role_messages(messages)
        elif "google" in model:
            # Alternating conversation roles
            messages = combine_successive_role_messages(messages)
            # Combine system message into first user message
            combined_system_msg = f"{messages[0]['content']}\n{messages[1]['content']}"
            messages = [{"role": "user", "content": combined_system_msg}] + messages[2:]
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        response = response.choices[0].message.content
    return response