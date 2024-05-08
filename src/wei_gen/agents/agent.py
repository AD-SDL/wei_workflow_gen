from .wrapper import *
from copy import deepcopy
from openai import OpenAI
import os
import json
from typing import Any, Dict, List, Union
from .prompts import INITIAL_ORCHESTRATION_PROMPT, INITIAL_CODE_PROMPT, INITIAL_VALIDATOR_PROMPT, INITIAL_WORKFLOW_PROMPT
from gen_workflow.db import DB


class Agent:
    def __init__(self, agent_type: str, model:str, config: Any, initial_prompt: List[Dict[str, str]]) -> None:
        self.agent_type: str = agent_type
        self.model: str = model # The model name
        self.initial_dialog_history: List[Dict[str, str]] = deepcopy(initial_prompt)
        self.config: Dict[str, Any] = config
        self.dialog_history: List[Dict[str, str]] = [] if not initial_prompt else deepcopy(initial_prompt)
        self.engine: Any = None
        self._initialize_engine()

        instrument_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../instruments.json")
        with open(instrument_path, "r") as f:
            self.all_instruments = json.load(f)

        self.all_instruments_str = json.dumps(self.all_instruments)

    def _initialize_engine(self) -> None:
        print(f"Initializing {self.agent_type} engine {self.model}")
        if "gpt" in self.model:
            self.engine = OpenAI(
                api_key=self.config["api_keys"]["openai"]["key"],
                organization=self.config["api_keys"]["openai"]["org"],
            )
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
            "gpt-3.5-turbo": lambda: openai_completion_with_backoff(
                engine=self.engine, model=self.model, messages=messages
            ),
            "gpt-3.5-turbo-0125": lambda: openai_completion_with_backoff(
                engine=self.engine, model=self.model, messages=messages
            ),
            "gpt-4": lambda: openai_completion_with_backoff(
                engine=self.engine, model=self.model, messages=messages
            ),
            "gpt-4-turbo": lambda: openai_completion_with_backoff(
                engine=self.engine, model=self.model, messages=messages
            ),
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
        return self.dialog_history[-1]["content"]

    def add_advice(self, content: str) -> None:
        new_message = {"role": "system", "content": content}
        self.dialog_history.append(new_message)

    def get_history(self) -> List[Dict[str, str]]:
        return self.dialog_history[1:] # Return everything but system prompt
    
    def set_history(self, history: List[Dict[str, str]]) -> None:
        self.dialog_history.extend(history)
        
class OrchestratorAgent(Agent):
    def __init__(self, model, config, agent_context=None):
        if agent_context:
            super().__init__("orchestration", model, config, agent_context)
        else:
            super().__init__("orchestration", model, config, INITIAL_ORCHESTRATION_PROMPT)

class CodeAgent(Agent):
    def __init__(self, model, config):
        super().__init__("code", model, config, INITIAL_CODE_PROMPT)

    def generate_code(self, user_input: str, workflow: str) -> str:
        prompt = f"Create a yaml workflow for the following experiment plan. {user_input} ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Here are examples of similar workflows \n{example_workflows}\n, you must follow this format"
        response = self.call(user_input)
        return response


class WorkflowAgent(Agent):
    def __init__(self, model, config):
        super().__init__("workflow", model, config, INITIAL_WORKFLOW_PROMPT)
        self.db = DB()
        
    def determine_instruments(self, user_input: str) -> str:
        instruments = self.db.query(user_input)
        prompt = f"Based on the following experiment plan, {user_input}, which instruments would you use? The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Here are examples of similar workflows \n{instruments}\n, you must follow this format"
        response = self.call(prompt)
        return response
    
    def determine_number_of_workflows(self, user_input: str) -> str:
        number_of_workflows = self.db.query(user_input)
        prompt = f"Based on the following experiment plan, {user_input}, how many workflows would you generate? The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Here are examples of similar workflows \n{number_of_workflows}\n, you must follow this format"
        response = self.call(prompt)
        return response
    
    def gen_workflow(self, user_input: str) -> str:
        example_workflows = self.db.query(user_input)
        prompt = f"Create a yaml workflow for the following experiment plan. {user_input} ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Here are examples of similar workflows \n{example_workflows}\n, you must follow this format"
        response = self.call(prompt)
        return response


class ValidatorAgent(Agent):
    def __init__(self, model, config):
        super().__init__("validator", model, config, INITIAL_VALIDATOR_PROMPT)
