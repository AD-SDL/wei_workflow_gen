import openai
import json
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed
from typing import List

# Constants
STOP_AFTER_ATTEMPT = 4
WAIT_SHORT = 3
WAIT_LONG = 5


# Retry Decorator for API Calls
def api_call_with_retry(func):
    @retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
           wait=wait_chain(*[wait_fixed(WAIT_SHORT) for _ in range(2)] + 
                           [wait_fixed(WAIT_LONG)]))
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@api_call_with_retry
def openai_completion_with_backoff(engine, model, messages):
    """OpenAI API wrapper"""
    res = engine.chat.completions.create(model=model, messages=messages, logprobs=True, top_logprobs=5)
    return res

# def llama_completion_with_backoff(engine, max_gen_len, temperature, top_p, messages: List[Dialog]):
#     """Local Llama API wrapper"""
#     messages_arr: List[Dialog] = []
#     new_messages = []
#     for msg in messages:
#         new_messages.append(
#             {"role": str(msg["role"]),
#              "content": str(msg["content"])
#             }
#         )
#     messages_arr.append(new_messages)
#     res = engine.chat_completion(
#         messages_arr,  # type: ignore
#         max_gen_len=max_gen_len,
#         temperature=temperature,
#         top_p=top_p,
#     )
#     return res


# def convert_openai_to_llama_format(messages):
#     llama_prompt = []
#     inital_prompt = messages[0]["content"] + " " + messages[1]["content"]
#     start_idx = 2
#     new_llama_msg = {
#         "role": "system",
#         "content": inital_prompt
#     }
#     llama_prompt.append(new_llama_msg)
#     for msg in messages[start_idx:]:
#         llama_prompt.append(msg)
#     return llama_prompt
