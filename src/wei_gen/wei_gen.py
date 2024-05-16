import yaml
from agents.agent import FrameworkAgent
from gen.gen_env import WorkflowGen, ConfigGen, CodeGen
from history.interface import History
from typing import Optional, Dict, Any

class Session:
    def __init__(self, config: Dict[str, Any], session_id: Optional[str] = None):
        """
        Initialize the session
        """
        self.history = History("0.0.1", session_id)
        self.version: str = "0.0.1" # TODO load from toml or similar

        self.framework: FrameworkAgent = FrameworkAgent(config)
        
        # load with history if session_id is provided
        if session_id:
            self.framework = FrameworkAgent(config, self.history.agent_context)
                
        self.workflow_gen_env: WorkflowGen = WorkflowGen(config,)
        self.config_gen_env: ConfigGen = ConfigGen(config)
        self.code_gen_env: CodeGen = CodeGen(config)
        self.validation_threshold: float = config["settings"]["validation_threshold"]

    def execute_experiment(self, user_input: str) -> None:
        """
        Execute the experiment
        """
        self.history.set_original_user_input(user_input)
        prob = self.framework.validate_experiment(user_input)
        if prob < self.validation_threshold:
            raise Exception(f"Experiment is not valid. Validator returned a probability < {self.validation_threshold} ({prob}). Check modules available and try again.")
        self.history.set_validation_status(True)

        experiment_framework = self.gen_experiment_framework(user_input)
        self.history.add_agent_history("framework", self.framework.ctx, experiment_framework)

        workflow = self.workflow_gen_env.generate_code(experiment_framework)
        self.history.add_agent_history("workflow", self.workflow_gen_env.ctx, workflow)


        code = self.code_gen_env.generate_code(experiment_framework, workflow)
        self.history.add_agent_history("code", self.code_gen_env.ctx, code)

        config = self.config_gen_env.generate_code(experiment_framework)
        self.history.add_agent_history("config", self.config_gen_env.ctx, config)

        print("Experiment completed successfully.")

    def call_gen_env(self, agent: str, user_input: str) -> str:
        """
        Call the generator environment
        """
        if agent == "framework":
            resp = self.framework_gen_env.call(user_input)
            self.history.add_agent_history("framework", self.framework_gen_env.ctx, resp)
            return resp
        elif agent == "workflow":
            resp = self.workflow_gen_env.call_coder(user_input)
            self.history.add_agent_history("workflow", self.workflow_gen_env.ctx, resp)
            return resp
        elif agent == "config":
            resp = self.config_gen_env.call_coder(user_input)
            self.history.add_agent_history("config", self.config_gen_env.ctx, resp)
            return resp
        elif agent == "code":
            resp = self.code_gen_env.call_coder(user_input)
            self.history.add_agent_history("code", self.code_gen_env.ctx,resp)
            return resp
        else:
            pass # TODO raise exception
        
    def modify_generated_data(self, agent: str, user_input: str) -> None:
        """
        Modify the generated data
        """
        self.history.update_generated_content(agent, user_input)

class WEIGen:
    def __init__(self, config_path: str):
        try:
            with open(config_path, "r") as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading the YAML file: {e}")
    
    def new_session(self) -> Session:
        return Session(self.config)
    
    def load_session(self, session_id: str) -> Session:
        return Session(self.config, session_id)
