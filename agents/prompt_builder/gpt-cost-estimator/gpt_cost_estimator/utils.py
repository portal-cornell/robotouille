import tiktoken

# This function has been taken from the GPT Cookbook shared by OpenAI under the MIT license:
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb
def num_tokens_from_messages(messages, model):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "o4-mini",
        "o4-mini-2025-04-16",
        "gpt-4o-mini",
        "gpt-4o-2024-08-06",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-0613",
        "gpt-3.5-turbo-0613",
        "gpt-4-1106-preview",
        "gpt-4-1106-vision-preview",
        "gpt-4",
        "gpt-4-32k",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-instruct",
        "gpt-3.5-turbo-16k-0613",
        "whisper-1",
        "tts-1",
        "tts-hd-1",
        "text-embedding-ada-002-v2",
        "text-davinci:003",
        "text-ada-001",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens