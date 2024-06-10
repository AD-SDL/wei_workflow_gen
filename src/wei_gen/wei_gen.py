import yaml
from agents.agent import FrameworkAgent
from gen.gen_env import WorkflowGen, ConfigGen, CodeGen
from history.interface import History
from typing import Optional, Dict, Any
import time
class Session:
    def __init__(self, config: Dict[str, Any], session_id: Optional[str] = None):
        """
        Initialize the session
        """
        self.version: str = "0.0.1" # TODO load from toml or similar
        self.config = config
        self.validation_threshold: float = config["settings"]["validation_threshold"]


        self._handle_history(session_id)
    
    def _handle_history(self, session_id = None):
        
        self.history = History(self.version, session_id= session_id)
        self.session_id = self.history.session_id

        print(f"Session ID: {self.session_id} {self.history.v}")
        # TODO make this cleaner
        self.framework: FrameworkAgent = FrameworkAgent(self.config, self.history.v["framework_agent_ctx"]) 
        
        self.workflow_gen_env: WorkflowGen = WorkflowGen( self.config, self.history.v["workflow_agent_ctx"])
        self.code_gen_env: CodeGen = CodeGen(self.config, self.history.v["code_agent_ctx"])

        self.workflow_gen_env.set_code(self.history.v["generated_workflow"])
        self.code_gen_env.set_code(self.history.v["generated_config"])
        
    

    def execute_experiment(self, user_description: str, user_values = None) -> None:
        """
        Execute the experiment
        """
        start_time = time.time()
        self.framework_step(user_description, user_values)
        self.workflow_step()
        self.code_step()
        self.config_step()
        print(f"Experiment completed successfully in {(time.time() - start_time):.2f} seconds")

 

    def framework_step(self, user_description, user_values):
        temp_start = time.time()
        print("Starting experiment...")
        self.history.set_user_inputs(user_description, user_values)
        is_valid, info = self.framework.validate_experiment(user_description)
        if not is_valid:
            raise Exception(f"Experiment is not valid. Validator returned a probability < {self.validation_threshold}. {info}")
        print(f"Experiment valid. Continuing...")

        experiment_framework = self.framework.gen_experiment_framework(user_description)
        self.history.add_agent_history("framework", self.framework.ctx, experiment_framework)
        print(f"Experiment Framework generated in {(time.time() - temp_start):.2f} seconds. Continuing...")

    
    def workflow_step(self):
        temp_start = time.time()
        workflow = self.workflow_gen_env.generate_code(self.history.get_generated("framework"))
        self.history.add_agent_history("workflow", self.workflow_gen_env.coder.ctx, workflow)
        print(f"Experiment Workflow generated  in {(time.time() - temp_start):.2f} seconds. Continuing...")

    def code_step(self):
        temp_start = time.time()
        code = self.code_gen_env.generate_code(self.history.get_generated("framework"), self.history.get_generated("workflow"))
        self.history.add_agent_history("code", self.code_gen_env.coder.ctx, code)
        print(f"Experiment Code generated in {(time.time() - temp_start):.2f} seconds. Continuing...")

    def config_step(self):
        config_instruments = self.workflow_gen_env.needs_config()
        if len(config_instruments) > 0:
            print(f"Config needed for {''.join(config_instruments)}. Continuing...", self.history.v)
            user_values = self.history.v["original_user_values"]
            framework = self.history.v["generated_framework"]
            for instrument in config_instruments:
                self.config_gen_env: ConfigGen = ConfigGen(self.config, instrument, self.history.v["config_agent_ctx"])
                config = self.config_gen_env.generate_code(framework, user_values)
                self.history.add_agent_history("config", self.config_gen_env.coder.ctx, config)

    def call_gen_env(self, agent: str, user_input: str) -> str:
        """
        Call the generator environment
        """
        # self._handle_history(session_id)
        if agent == "framework":
            resp = self.framework.call(user_input)
            if self.history.v["generated_framework"] != "":
                resp = None
            self.history.add_agent_history("framework", self.framework.ctx, resp)
            return resp
        elif agent == "workflow":
            resp = self.workflow_gen_env.call_coder(user_input)
            self.history.add_agent_history("workflow", self.workflow_gen_env.coder.ctx, self.workflow_gen_env.code)
            return resp
        elif agent == "config":
            resp = self.config_gen_env.call_coder(user_input)
            self.history.add_agent_history("config", self.config_gen_env.coder.ctx, self.config_gen_env.code)
            return resp
        elif agent == "code":
            resp = self.code_gen_env.call_coder(user_input)
            self.history.add_agent_history("code", self.code_gen_env.coder.ctx, self.code_gen_env.code)
            return resp
        else:
            pass # TODO raise exception


    def modify_generated_data(self, agent: str, user_input: str) -> None:
        """
        Modify the generated data
        """
        self.history.update_generated(agent, user_input)
    
    def get_history(self) -> Dict[str, Any]:
        """
        Get the history of the session
        """
        return self.history.v

class WEIGen:
    def __init__(self, config_path: str):
        try:
            with open(config_path, "r") as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading the YAML file: {e}")
    
    def new_session(self, session_id = None) -> Session:
        return Session(self.config, session_id)
