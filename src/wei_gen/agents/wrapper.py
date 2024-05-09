import openai
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed
from typing import List, Any, Callable, Dict

# Constants
STOP_AFTER_ATTEMPT: int = 4
WAIT_SHORT: int = 3
WAIT_LONG: int = 5


# Retry Decorator for API Calls
def api_call_with_retry(func: Callable) -> Callable:
    @retry(stop=stop_after_attempt(STOP_AFTER_ATTEMPT), 
           wait=wait_chain(*[wait_fixed(WAIT_SHORT) for _ in range(2)] + 
                           [wait_fixed(WAIT_LONG)]))
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    return wrapper

@api_call_with_retry
def openai_completion_with_backoff(engine: openai.ChatCompletion, model: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """OpenAI API wrapper"""
    res: Dict[str, Any] = engine.chat.completions.create(model=model, messages=messages, logprobs=True, top_logprobs=5)
    return res
