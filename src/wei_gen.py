import time
import yaml
from agents import OrchestratorAgent, CodeAgent, ValidatorAgent
class History:
    def __init__(self, version):
        """
        Initialize the history of the session
        """
        self.history = []
        self.agent_context = []
        self.text_context = ""
        self.version = version
        self.orchestration = ""
        self.status = {
            "orchestration": False,
            "code": False,
        }

    def add_history(self, agent_type, phase, content, agent_context):
        """
        Add a new entry to the session
        """
        new_history = {
            "agent_type": agent_type,
            "phase": phase,
            "content": content,
            "timestamp": time.time(),
            "index": len(self.history),
        }
        self.history.append(new_history)
        self.agent_context.append(agent_context)

        if len(self.context) > 0:
            self.context += "\n"
        self.text_context += agent_type + ": " + content


class Session:
    def __init__(self, config):
        """
        Initialize the session
        """
        self.history = History(config["version"])
        self.version = config["version"]
        self.start_time = time.time()

        self.orchestrator = OrchestratorAgent(config["orchestrator_model"], config)
        self.coder = CodeAgent(config["code_model"], config)
        self.validator = ValidatorAgent(config["validator_model"], config)

        # TODO - add logic to load the previous context from a previous session

    def gen_orchestration(self, user_input):
        """
        Orchestrate the experiment plan.
        """
        response = self.orchestrator.call(user_input)
        self.history.orchestration = response
        self.history.add_history("orchestrator", "orchestration", response)
        return response
    
    def complete_orchestration(self):
        """
        Mark the orchestration step as complete for the session
        """
        self.status["orchestration"] = True

    
    def gen_code(self, content):
        """
        Generate code (for the app, YAMLs, etc.)
        """
        # TODO - kick off the code generation loop
        # TODO - to start just do code gen without validation
        pass

    def complete_code(self):
        """
        Mark the code generation step as complete for the session
        """
        self.status["code"] = True
    
        




class WEIGen:
    # The entry point, will be used by the api and cli. Will also allow users to start and end sessions, or look at previous sessions.
    def __init__(self,config_path):
        try:
            with open(config_path, "r") as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading the YAML file: {e}")
            return None