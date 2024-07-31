import os
import random

from .constants import EXAMPLES_PATH

def retrieve_example(example_dir_path, num_examples, request_regex, response_regex):
    """Retrieves examples from the example directory.

    Parameters:
        example_dir_path (str)
            The relative path of the directory containing the in-context examples.
        num_examples (int)
            The number of examples to retrieve.
        request_regex (re.Pattern)
            The regex pattern for the request.
        response_regex (re.Pattern)
            The regex pattern for the response.
        
    Returns:
        examples (List[Dict[str, str]])
            The examples to query the LLM with.
    """
    example_path = os.path.join(EXAMPLES_PATH, example_dir_path)
    example_files = os.listdir(example_path)
    sampled_files = random.sample(example_files, max(num_examples, len(example_files)))
    examples = []
    for file_name in sampled_files:
        with open(os.path.join(example_path, file_name), "r") as file:
            text = file.read()
            requests = request_regex.findall(text)
            responses = response_regex.findall(text)
        example = []
        for request, response in zip(requests, responses):
            user_msg = {"role": "user", "content": request}
            agent_msg = {"role": "assistant", "content": response}
            example += [user_msg, agent_msg]
        examples += example
    return examples
    