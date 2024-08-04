from .wrapper import *
from copy import deepcopy
from openai import OpenAI
import numpy as np
import os
import json
from typing import Any, Dict, List, Union
from .prompts import INITIAL_ORCHESTRATION_PROMPT, INITIAL_CODE_PROMPT, INITIAL_VALIDATOR_PROMPT, INITIAL_WORKFLOW_PROMPT, INITIAL_INSTRUMENT_PROMPT, STEPS_EXAMPLE_JSON
from rag.interface import RAG
from z3 import *

class Agent:
    def __init__(self, agent_type: str, config: Any, initial_prompt: List[Dict[str, str]]) -> None:
        self.agent_type: str = agent_type
        self.model: str = config["settings"][f"{agent_type}_model"] if "config" not in agent_type else config["settings"]["config_model"]
        self.initial_ctx: List[Dict[str, str]] = deepcopy(initial_prompt)
        self.config: Dict[str, Any] = config
        self.ctx: List[Dict[str, str]] = [] if not initial_prompt else deepcopy(initial_prompt)
        self.engine: Any = None
        self._initialize_engine()
        print(agent_type,self.ctx)

        instrument_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../instruments.json")
        with open(instrument_path, "r") as f:
            self.all_instruments = json.load(f)

        self.all_instruments_str = json.dumps(self.all_instruments)

    def _initialize_engine(self) -> None:
        print(f"Initializing {self.agent_type} engine {self.model}")
        if "gpt" in self.model:
            self.engine = OpenAI(
                api_key=self.config["api_keys"]["openai"]["key"],
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
    def _get_context(self, initial_ctx, loaded_ctx):
        return loaded_ctx if loaded_ctx else initial_ctx
    
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
             "gpt-4o": lambda: openai_completion_with_backoff(
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
        response = self.call_engine(history, raw)
        return response
    
    def parse_logprobs(self, resp: Any, target_string: str = "YES") -> float:
        """
        Parse the logprobs to get the probability of the response being yes (or whatever string specified)
        """
        top_logprobs = resp.choices[0].logprobs.content[0].top_logprobs
        p_target = 0
        for entry in top_logprobs:
            if entry.token.upper() == target_string:
                p_target += np.exp(entry.logprob)
        # p_target = sum(np.exp(entry.logprob) for entry in top_logprobs if entry.token.upper() == target_string)
        # Convert log probability to actual 0 - 1 probability using np.exp
        return p_target
    
class FrameworkAgent(Agent):
    def __init__(self, config, loaded_ctx=None):
        super().__init__("framework", config, self._get_context(INITIAL_ORCHESTRATION_PROMPT, loaded_ctx))
 
    
    def validate_experiment(self, user_input: str):
        """
        Validate if the experiment can be carried out with the modules available from the /abouts
        """
        base_prompt = f"Based on the following experiment proposition, {user_input}, can the instruments you have perform this experiment? The following is list of all tools at your disposal {self.all_instruments_str}, YOU CAN ONLY USE THESE INSTRUMENTS"
        prompt = base_prompt + " ##### IMPORTANT: You must ONLY respond in a YES or NO to this question. Can you carry on with this experiment?"
        resp = self.transient_call(prompt, True)
        prob = self.parse_logprobs(resp)
        if float(prob) < 0.001:
            return False, self._explain_prev_response(base_prompt)
        return True, prob
    
    def _explain_prev_response(self, prev_experiment) -> str:
        """
        Explain the previous response
        """
        prompt = f"{prev_experiment}\n##### The proposal above failed. Can you explain why?"
        return self.transient_call(prompt)
    
    def gen_experiment_framework(self, user_input: str) -> str:
        prompt = f"Create a step by step plan of the following experiment {user_input} ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS. Make sure to break down large objectives into a smaller, granular tasks. Your responses should always be clear and concise, your should ONLY respond with this step by step plan."
        max_tries = 3
        framework =  self.call(prompt)
        for _ in range(max_tries):
            instrument_json = self._extract_instrument_order(framework)
            solver, instrument_vars = self.json_to_z3_script(instrument_json)  
            success, result = self.execute_z3_script(solver, instrument_vars)
            print(success, result)
            if success:
                return framework
            
            # Try generation again
            prompt_retry = f"The previous framework failed to be validate due to there not being a logical flow of steps between the different instruments. Ensure that objects move between instruments in logical order."
            framework = self.call(prompt_retry)
        return "Failed to generate a valid experiment plan. Please try again."

    def _extract_instrument_order(self, framework) -> str:
        prompt = f"Can you distill this experiment plan an simple order of operations? make sure that there is a transportation instruction for moving items around the lab, such as use of the pf400 to move a plate between robots ##### The following is list of all instruments at your disposal {self.all_instruments_str}, YOU MUST ONLY USE THESE INSTRUMENTS ##### {framework} ##### IMPORTANT: You must ONLY respond in json format, example: {STEPS_EXAMPLE_JSON}."
        json_instruments =  self.transient_call(prompt)
        return json_instruments
    
    def json_to_z3_script(self, json_text: str):
        json_text = json_text.replace("```json", "").replace("```", "")
        data = json.loads(json_text)
        s = Solver()
        prev_instrument = None
        instrument_vars = {}

        for i, step in enumerate(data['steps']):
            # current_action = step['action']
            current_instrument = step['instrument']

            # Add the instrument to the variables if not already added
            if current_instrument not in instrument_vars:
                instrument_vars[current_instrument] = Bool(f"use_{current_instrument}")

            if prev_instrument and prev_instrument != current_instrument:
                transfer_exists = Bool(f"transfer_{prev_instrument}_to_{current_instrument}_{i}")
                s.add(transfer_exists)
                s.add(Implies(transfer_exists, And(instrument_vars[prev_instrument], instrument_vars[current_instrument])))

            prev_instrument = current_instrument

        return s, instrument_vars

    def execute_z3_script(self, solver, instrument_vars):
        """Executes the Z3 solver and returns the results."""
        if solver.check() == sat:
            model = solver.model()
            result = {str(var): model[var] for var in instrument_vars.values() if model[var]}
            return True, result
        else:
            return False, "No solution exists with the given constraints."


class CodeAgent(Agent):
    def __init__(self, config, loaded_ctx=None):
        super().__init__("code", config, self._get_context(INITIAL_CODE_PROMPT, loaded_ctx) )

    def gen_code(self, experiment_framework: str, workflow: str) -> str:
        prompt = f"Create a python file for running this yaml workflow {workflow}. This is the experiment that this python code should run (using this workflow) {experiment_framework}"
        return self.call(prompt)
    
    def get_code(self) -> str:
        # gets the code from the previous message
        prompt = "Return ONLY the generated python code"
        return self.transient_call(prompt)

class ValidatorAgent(Agent):
    def __init__(self, config, loaded_ctx=None):
        super().__init__("validator", config, self._get_context(INITIAL_VALIDATOR_PROMPT, loaded_ctx))

class WorkflowAgent(Agent):
    def __init__(self, config, loaded_ctx=None):
        super().__init__("workflow", config, self._get_context(INITIAL_WORKFLOW_PROMPT, loaded_ctx))
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



class ConfigAgent(Agent):
    def __init__(self, config, instrument, loaded_ctx=None): #OT2 Liquidhandling robot
        print("loaded_ctx", loaded_ctx, instrument)
        super().__init__(f"config_{instrument}", config, self._get_context(INITIAL_INSTRUMENT_PROMPT, loaded_ctx))
        self.rag = RAG(instrument)
        self.instrument = instrument

    def gen_instrument_config(self, experiment_framework, user_values=None) -> str:
        n_results = 3
        example_configs = self.rag.query(experiment_framework, n_results=n_results)
        extra_context = f"Use the following values {user_values} as context for desired values in the config. " if user_values else ""
        prompt = f"You are creating a yaml config for the {self.instrument} instrument which will be used in the following experiment {experiment_framework}. {extra_context}Use the following {n_results} examples to construct your config\n{example_configs}\n #### IMPORTANT: You must respond exclusively with ONLY A YAML FILE."
        return self.call(prompt)

class AdviceAgent(Agent):
    def __init__(self, config, aid_type, loaded_ctx=None):
        super().__init__(f"aid-{aid_type}", config, [])
        self.aid_type = aid_type

    def provide_advice(self,history, user_input: str) -> str:
        self.ctx = {
            "role": "system",
            "content": f"Here is some advice for you. {history}" # TODO import this
        }
        messages = list(self.ctx)
        response = self.call_engine(messages)
        store = {"role": "assistant", "content": response}
        self.ctx.append(store)
        return response