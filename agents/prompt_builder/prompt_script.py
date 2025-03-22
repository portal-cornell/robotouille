"""
This script queries the LLM with an existing prompt and a user provided prompt.

To run this script on an example, run the following command in the terminal:
    python prompt_script.py \
        --user_prompt "Please calculate the following: (100 + 12) * 24 / 2^6" \
        --experiment_name prompt_script_test \
        --prompt_description calculator \
        --prompt_version 1.0.0
"""
import argparse

from constants import PROMPT_HISTORY_PATH
from prompt_llm import prompt_llm, get_accumulated_cost
import serializer
import utils

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--user_prompt", required=True, help="The user prompt to prompt the LLM with.")
    argparser.add_argument("--experiment_name", required=True, help="The name of the experiment for the prompt.")
    argparser.add_argument("--prompt_description", required=True, help="The description of the prompt to test.")
    argparser.add_argument("--prompt_version", required=True, help="The version of the prompt to test.")
    argparser.add_argument("--model", default="gpt-3.5-turbo-0125", help="The LLM model to query.")
    argparser.add_argument("--temperature", default=0.0, type=float, help="The LLM temperature.")
    argparser.add_argument("--max_attempts", default=10, type=int, help="The number of attempts to query the LLM before giving up")
    argparser.add_argument("--debug", action="store_true", help="Whether or not to mock an LLM response")
    argparser.add_argument("--sleep_time", default=5, type=int, help="The number of seconds to sleep after a failed query before requerying")
    argparser.add_argument("--completion_tokens", default=1, type=int, help="The number of completion tokens to mock query the LLM with.")
    args = argparser.parse_args()

    # Retrieve the prompt, serialize it into messages, and prompt the LLM for a response
    prompt_path = utils.get_prompt_path(PROMPT_HISTORY_PATH, args.experiment_name, args.prompt_description, args.prompt_version)
    messages = serializer.serialize_into_messages(prompt_path)
    response = prompt_llm(
        args.user_prompt,
        messages,
        args.model,
        args.temperature,
        max_attempts=args.max_attempts,
        sleep_time=args.sleep_time,
        debug=args.debug,
        mock=args.debug,
        completion_tokens=args.completion_tokens
    )
    print(response)
    print(f"Cost: {get_accumulated_cost()}")