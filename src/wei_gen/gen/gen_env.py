import subprocess
import os
from openai import OpenAI
from agents.agent import CodeAgent, ValidatorAgent, WorkflowAgent, ConfigAgent
from typing import Tuple
class GenEnv:
    def __init__(self, config, coder, validator):
        self.config = config
        self.coder = coder
        self.validator = validator
    
        self.code = ""
        self.test_code = ""
        self.max_attempts = 3

        self.ctx ={
            "coder": [],
            "validator": []
        }

    def call_coder(self, user_input):
        return self.coder.call_engine(user_input)
    
    def generate_code(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

class WorkflowGen(GenEnv):
    def __init__(self, config, loaded_code_ctx):
        coder: WorkflowAgent = WorkflowAgent(config, loaded_code_ctx)
        super().__init__(config, coder, None)

    def _is_workflow_valid(self) -> Tuple[bool, str]:
        # TODO: use pydantic to validate the workflow
        # TODO: return any errors
        return True, ""
    
    def _handle_errors(self, err):
        print("Handling errors based on the feedback...")
        response = self.call_coder(f"Please fix the following error in the code: {err}\n IMPORTANT: You most ONLY respond with the corrected code.")
        self.code = response

    def generate_code(self, experiment_framework):
        self.code = self.coder.gen_workflow(experiment_framework)
        is_valid, err = self._is_workflow_valid()
        attempts = 0
        while not is_valid:
            if attempts >= self.max_attempts:
                # handle if max attempts reached for code gen, append error message to yaml
                self.code += f"\n# Failed to generate a valid workflow after {self.max_attempts} attempts. Please review the workflow manually. Error: {err}"
                break
            self._handle_errors(err)
            is_valid, err = self._is_workflow_valid()
            attempts += 1
        self.ctx["coder"] = self.coder.ctx
        return self.code
    
    def needs_config(self) -> list:
        config_instruments = []
        for module in self.config["needs_config"]:
            if module in self.code:
                config_instruments.append(module)
        return config_instruments
    
class ConfigGen(GenEnv):
    def __init__(self, config, instrument):
        coder: ConfigAgent = ConfigAgent(config, instrument)
        super().__init__(config, coder, None)

    def generate_code(self, experiment_framework, user_values):
        self.code = self.coder.gen_instrument_config(experiment_framework, user_values)
        self.ctx["coder"] = self.coder.ctx
        return self.code


class CodeGen(GenEnv):
    def __init__(self, config, loaded_code_ctx):
        coder: CodeAgent = CodeAgent(config, loaded_code_ctx)
        validator: ValidatorAgent = ValidatorAgent(config)
        super().__init__(config, coder, validator)

    def generate_code(self, experiment_framework, workflow):
        full_resp = self.coder.gen_code(experiment_framework, workflow)
        self.code = self.coder.get_code()
        self.ctx["coder"] = self.coder.ctx
        return self.code
    



        # TODO, create mocks of some sort to test logic of generated python code.
        # self.test_code = self.validator.generate_tests(description, self.code)

    # def _test_code(self):
        # # save code into a temp file
        # with open('temp_code.py', 'w') as file:
        #     file.write(self.code + "\n" + self.test_code)


        # # This step should maybe actually do some sort of validation on the experiment
        # # Like running in RViz or something
        # try:
        #     result = subprocess.run(['python', 'temp_code.py'], check=True, capture_output=True, text=True)
        #     print("Test Passed. Output:\n", result.stdout)
        # except subprocess.CalledProcessError as e:
        #     print("Test Failed. Error:\n", e.stderr)
        #     # Rerun code generation if tests fail
        #     self.handle_errors(e.stderr)
        
