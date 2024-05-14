from .wrapper import *
from copy import deepcopy
from openai import OpenAI
import numpy as np
import os
import json
from typing import Any, Dict, List, Union
from .prompts import INITIAL_ORCHESTRATION_PROMPT, INITIAL_CODE_PROMPT, INITIAL_VALIDATOR_PROMPT, INITIAL_WORKFLOW_PROMPT, INITIAL_INSTRUMENT_PROMPT
from wei_gen.rag.interface import RAG


class Agent:
    def __init__(self, agent_type: str, config: Any, initial_prompt: List[Dict[str, str]]) -> None:
        self.agent_type: str = agent_type
        self.model: str = config["settings"][f"{agent_type}_model"] if "instrument" not in agent_type else config["settings"]["instrument_model"]
        self.initial_ctx: List[Dict[str, str]] = deepcopy(initial_prompt)
        self.config: Dict[str, Any] = config
        self.ctx: List[Dict[str, str]] = [] if not initial_prompt else deepcopy(initial_prompt)
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
        self.ctx = deepcopy(self.initial_ctx)

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
            if raw: # for when logprobs are needed
                return response
            return self._parse_response(self.model, response)
        else:
            raise ValueError(f"Unknown model {self.model}")

    def call(self, prompt: str) -> str:
        if prompt:
            prompt_entry = {"role": "user", "content": prompt}
            self.ctx.append(prompt_entry)

        messages = list(self.ctx)
        message = self.call_engine(messages)
        store = {"role": "assistant", "content": message}
        self.ctx.append(store)
        return message

    def last_response(self) -> str:
        return self.ctx[-1]["content"]

    def add_advice(self, content: str) -> None:
        new_message = {"role": "system", "content": content}
        self.ctx.append(new_message)

    def get_history(self) -> List[Dict[str, str]]:
        return self.ctx[1:] # Return everything but system prompt
    
    def set_history(self, history: List[Dict[str, str]]) -> None:
        self.ctx.extend(history)

    def transient_call(self, prompt: str, raw: bool = False) -> str:
        """
        transient_call is used to make a call to the engine without updating the context history
        """
        history = deepcopy(self.ctx)
        history.append({"role": "user", "content": prompt})
        return self.call_engine(list(history), raw).lower()
    
    def parse_logprobs(self, resp: Any, target_string: str = "YES") -> float:
        """
        Parse the logprobs to get the probability of the response being yes (or whatever string specified)
        """
        top_logprobs = resp.choices[0].logprobs.content[0].top_logprobs
        p_target = sum(entry.logprob for entry in top_logprobs if entry.token.upper() == target_string)

        # Convert log probability to actual 0 - 1 probability using np.exp
        return np.exp(p_target)
    
class OrchestratorAgent(Agent):
    def __init__(self, config, agent_context=None):
        if agent_context:
            super().__init__("orchestrator", config, agent_context)
        else:
            super().__init__("orchestrator", config, INITIAL_ORCHESTRATION_PROMPT)
    
    def validate_experiment(self, user_input: str) -> str:
        """
        Validate if the experiment can be carried out with the modules available from the /abouts
        """
        prompt = f"Based on the following experiment plan, {user_input}, can you tools at your disposal actually carry out this experiment? The following is list of all tools at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### IMPORTANT: You must ONLY respond in a YES or NO to this question."
        resp = self.transient_call(prompt, True)
        return self.parse_logprobs(resp)
    
    def gen_experiment_framework(self, user_input: str) -> str:
        prompt = f"Create a step by step plan . {user_input} ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Here are examples of similar workflows \n{example_workflows}\n, you must follow this format"
        return self.call(prompt)

class CodeAgent(Agent):
    def __init__(self, config):
        super().__init__("code", config, INITIAL_CODE_PROMPT)

    def gen_code(self, experiment_framework: str, workflow: str) -> str:
        prompt = f"Create a python file for running this yaml workflow {workflow}. This is the experiment that this python code should run (using this workflow) {experiment_framework}"
        return self.call(prompt)
    
    def get_code(self) -> str:
        # gets the code from the previous message
        prompt = "Return ONLY the generated python code"
        return self.transient_call(prompt)

class ValidatorAgent(Agent):
    def __init__(self, config):
        super().__init__("validator", config, INITIAL_VALIDATOR_PROMPT)

class WorkflowAgent(Agent):
    def __init__(self, config):
        super().__init__("workflow", config, INITIAL_WORKFLOW_PROMPT)
        self.rag = RAG()

    def _determine_instruments(self, experiment_framework: str) -> str:
        prompt = f"Before creating the workflow, first determine the instruments you will need based on the following experiment plan, {experiment_framework}. The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### Now, create a list of instruments you will need for this experiment, you must ONLY respond with a list of instruments."
        return self.transient_call(prompt)
    
    def gen_workflow(self, experiment_framework: str) -> str:
        suggested_instruments = self._determine_instruments(experiment_framework)
        example_workflows = self.rag.query(experiment_framework)
        prompt = f"Create a yaml workflow for the following experiment plan. {experiment_framework} ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS. Some suggested instruments to use are: {suggested_instruments}. The following are examples of workflows created for similar experiments:\n{example_workflows}\n #### IMPORTANT: You must respond exclusively with ONLY A YAML FILE."
        return self.call(prompt)
    
    # def determine_number_of_workflows(self, user_input: str) -> str:
    #     number_of_workflows = self.db.query(user_input)
    #     example_of_multiple_workflows = """Here is an example of a multiple workflow system
    #     mixcolor_workflow: # handles mixing colors
    #         - use pf400 to move plate from camera to mixer
    #         - use ot2_cp_gamma to mix colors
    #         - use pf400 to move plate to camera
    #         - use camera_module to take a picture
    #     new_plate_workflow: # handles creating a new plate
    #         - use sciclops to get plate to plate exchange
    #         - use pf400 to get plate to final location
    #     replenish_workflow: # handles replenishing the stock
    #         - refill ink with barty

    #     This type of structure allows different workflows to be called in a modular way, and is helpful for experiments where there is a lot of repeated steps.
    #     """ 
    #     prompt = f"Based on the following experiment plan, {user_input}, will you need to create more than one workflow? The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### {example_of_multiple_workflows} ##### IMPORTANT: You must ONLY respond in a YES or NO to this question."
    #     response = self.call(prompt)
    #     return response



class InstrumentAgent(Agent):
    def __init__(self, config, instrument): #OT2 Liquidhandling robot
        super().__init__(f"instrument-{instrument}", config, INITIAL_INSTRUMENT_PROMPT)
        self.rag = RAG(instrument)
        self.instrument = instrument

    def gen_instrument_config(self, experiment_framework, extra_context=None) -> str:
        n_results = 3
        example_configs = self.rag.query(experiment_framework, n_results=n_results)
        extra_context = f"Use the following values {extra_context} as context for desired values in the config. " if extra_context else ""
        prompt = f"You are creating a yaml config for the {self.instrument} instrument which will be used in the following experiment {experiment_framework}. {extra_context}Use the following {n_results} examples to construct your config\n{example_configs}\n #### IMPORTANT: You must respond exclusively with ONLY A YAML FILE."
        return self.call(prompt)
