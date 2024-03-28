from wrapper import *
# from prompts import seller_gen
# from prompts import buyer_gen
from copy import deepcopy
from openai import OpenAI

from typing import Any, Dict, List, Union
from prompts import INITIAL_ORCHESTRATION_PROMPT, INITIAL_CODE_PROMPT, INITIAL_VALIDATOR_PROMPT

class Agent:
    def __init__(self, agent_type: str, model: str, config: Any, initial_prompt: List[Dict[str, str]]) -> None:
        self.agent_type: str = agent_type
        self.model: str = model  # The model name
        self.initial_dialog_history: List[Dict[str, str]] = deepcopy(initial_prompt)
        self.config: Dict[str, Any] = config
        self.dialog_history: List[Dict[str, str]] = [] if not initial_prompt else deepcopy(initial_prompt)
        self.engine: Any = None
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        print(f"Initializing {self.agent_type} engine {self.model}")
        if "gpt" in self.model:
            self.engine = OpenAI(api_key=self.config["api_keys"]["openai"]["key"],
                                 organization=self.config["api_keys"]["openai"]["org"])
        else:
            raise ValueError(f"Unknown model {self.model}")

    def reset(self) -> None:
        self.dialog_history = deepcopy(self.initial_dialog_history)

    def _parse_response(self, engine: str, response: Any) -> str:
        if "gpt" in engine:
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unknown engine {engine}")

    def call_engine(self, messages: List[Dict[str, str]], raw: bool = False) -> Any:
        model_router = {
            "gpt-3.5-turbo": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
            "gpt-3.5-turbo-0125": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
            "gpt-4": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
        }
        if self.model in model_router:
            response = model_router[self.model]()
            if raw:
                return response
            return self._parse_response(self.model, response)
        else:
            raise ValueError(f"Unknown model {self.model}")

    def call(self, prompt: str) -> str:
        if prompt:
            prompt_entry = {"role": "user", "content": prompt}
            self.dialog_history.append(prompt_entry)
        
        messages = list(self.dialog_history)
        message = self.call_engine(messages)
        store = {"role": "assistant", "content": message}
        self.dialog_history.append(store)
        return message

    def last_response(self) -> str:
        return self.dialog_history[-1]['content']

    def add_advice(self, content: str) -> None:
        new_message = {"role": "system", "content": content}
        self.dialog_history.append(new_message)




class OrchestratorAgent(Agent):
    def __init__(self, config):
        super().__init__("orchestration", config, INITIAL_ORCHESTRATION_PROMPT)

class CodeAgent(Agent):
    def __init__(self, config):
        super().__init__("code", config, INITIAL_CODE_PROMPT)

class ValidatorAgent(Agent):
    def __init__(self, config):
        super().__init__("validator", config, INITIAL_VALIDATOR_PROMPT)