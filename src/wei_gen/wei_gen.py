import time
import yaml
import json
from agents.agent import OrchestratorAgent, CodeAgent, ValidatorAgent
import uuid
import os
class History:
    def __init__(self, version, session_id=None):
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
        self.session_id = session_id if session_id else str(uuid.uuid4())
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Define the path to the JSON file
        self.history_file_path = f"{base_dir}/history/{self.session_id}_history.json"
        
        if session_id:
            # If there's a session_id, try to load the existing history
            loaded_data = self.load_history()
            self.history =loaded_data["history"]
            self.agent_context = loaded_data["agent_context"]
            self.text_context = loaded_data["text_context"]
            self.orchestration = loaded_data["orchestration"]
            self.status = loaded_data["status"]
            self.session_id = loaded_data["session_id"]




    def load_history(self):
        """
        Load history from a JSON file
        """
        try:
            
            with open(self.history_file_path, 'r') as file:
                return  json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, start with an empty history
            print("error")

    def save_history(self):
        """
        Save the current history to a JSON file
        """
        with open(self.history_file_path, 'w') as file:
            entry = {
                "version": self.version,
                "history": self.history,
                "agent_context": self.agent_context,
                "text_context": self.text_context,
                "orchestration": self.orchestration,
                "status": self.status,
                "session_id": self.session_id,
            }
            json.dump(entry, file, indent=4)

        

    def add_history(self, agent_type, phase, content,agent_context):
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
        self.agent_context = agent_context
        if "#####" in content:
            orchestration = content.split("#####")[1]
            self.orchestration = orchestration
        if len(self.text_context) > 0:
            self.text_context += "\n"
        self.text_context += agent_type + ": " + content
        self.save_history()
        print( "HISTORY", self.history,"\nAGENT",self.agent_context, "\nTEXT",self.text_context, "\nORCHESTRATION",self.orchestration)


class Session:
    def __init__(self, config, session_id=None):
        """
        Initialize the session
        """
        self.history = History(config["version"], session_id)
        self.version = config["version"]
        self.start_time = time.time()
        settings = config["settings"]
        self.orchestrator = OrchestratorAgent(settings["orchestrator_model"], config)
        if session_id:
            self.orchestrator = OrchestratorAgent(settings["orchestrator_model"], config, self.history.agent_context)
        
        self.coder = CodeAgent(settings["code_model"], config)
        self.validator = ValidatorAgent(settings["validator_model"], config)


    def gen_orchestration(self, user_input):
        """
        Orchestrate the experiment plan.
        """
        response = self.orchestrator.call(user_input)
        self.history.orchestration = response
        self.history.add_history("orchestrator", "orchestration", response, self.orchestrator.dialog_history)
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
    def new_session(self):
        return Session(self.config)
    
    def load_session(self, session_id):
        return Session(self.config, session_id)
    
