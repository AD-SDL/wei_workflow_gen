import subprocess
import os
from openai import OpenAI
from agents.agent import CodeAgent, ValidatorAgent

class CodeGenEnv:
    def __init__(self, config):
        settings = config["settings"]
        self.code = ""
        self.test_code = ""
        self.coder: CodeAgent = CodeAgent(settings["code_model"], config)
        self.validator: ValidatorAgent = ValidatorAgent(settings["validator_model"], config)

    def generate_code_and_tests(self, description):
        self.code = self.coder.generate_code(description)
        self.test_code = self.validator.generate_tests(description, self.code)

    def test_code_execution(self):
        # save code into a temp file
        with open('temp_code.py', 'w') as file:
            file.write(self.code + "\n" + self.test_code)


        # This step should maybe actually do some sort of validation on the experiment
        # Like running in RViz or something
        try:
            result = subprocess.run(['python', 'temp_code.py'], check=True, capture_output=True, text=True)
            print("Test Passed. Output:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Test Failed. Error:\n", e.stderr)
            # Rerun code generation if tests fail
            self.handle_errors(e.stderr)
        
    def handle_errors(self, error):
        print("Handling errors based on the feedback...")

        self.generate_code_and_tests("Please fix the following error in the code: " + error, self.code)

