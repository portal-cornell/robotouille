"""
This module acts as a wrapper for OpenAI's chat API.
"""
import os
import time

import openai
from openai.types.chat.chat_completion import ChatCompletion
openai.api_key = os.getenv("OPENAI_API_KEY")

from gpt_cost_estimator import CostEstimator

import logging
logger = logging.getLogger(__name__)

def get_openai_llms():
    """Returns the available OpenAI LLMs compatible with the Chat API.

    Returns:
        openai_llm_names (List[str])
            The available OpenAI LLMs compatible with the Chat API.
    """
    client = openai.OpenAI()
    openai_models = client.models.list()
    openai_llm_names = [model.id for model in openai_models if 'gpt' in model.id]
    return openai_llm_names

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
            
    else:
        # TODO(chalo2000): Support open LLM models
        raise NotImplementedError(f"Model {model} is not supported.")
    return response