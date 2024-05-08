import time
import yaml
import json
from agents.agent import OrchestratorAgent, CodeAgent, ValidatorAgent, WorkflowAgent
import uuid
import os
from typing import Optional, Dict, List, Any
from gen_workflow.db import DB
class History:
    def __init__(self, version: str, session_id: Optional[str] = None):
        """
        Initialize the history of the session
        """
        self.history: List[Dict[str, Any]] = []
        self.agent_context: List[Any] = []
        self.text_context: str = ""
        self.version: str = version
        self.orchestration: str = ""
        self.status: Dict[str, bool] = {
            "orchestration": False,
            "code": False,
        }
        self.session_id: str = session_id if session_id else str(uuid.uuid4())
        base_dir: str = os.path.dirname(os.path.abspath(__file__))

        # Define the path to the JSON file
        self.history_file_path: str = f"{base_dir}/history/{self.session_id}_history.json"
        
        self.db = DB()
        if session_id:
            # If there's a session_id, try to load the existing history
            loaded_data: Dict[str, Any] = self.load_history()
            self.history = loaded_data["history"]
            self.agent_context = loaded_data["agent_context"]
            self.text_context = loaded_data["text_context"]
            self.orchestration = loaded_data["orchestration"]
            self.status = loaded_data["status"]
            self.session_id = loaded_data["session_id"]

        # You will need to modify assistant responses as iterations continue.

    def load_history(self) -> Dict[str, Any]:
        """
        Load history from a JSON file
        """
        try:
            with open(self.history_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Error: File not found.")
            return {}

    def save_history(self) -> None:
        """
        Save the current history to a JSON file
        """
        with open(self.history_file_path, 'w') as file:
            entry: Dict[str, Any] = {
                "version": self.version,
                "history": self.history,
                "agent_context": self.agent_context,
                "text_context": self.text_context,
                "orchestration": self.orchestration,
                "status": self.status,
                "session_id": self.session_id,
            }
            json.dump(entry, file, indent=4)

    def add_history(self, agent_type: str, phase: str, content: str, agent_context: List[Any]) -> None:
        """
        Add a new entry to the session
        """
        new_history: Dict[str, Any] = {
            "agent_type": agent_type,
            "phase": phase,
            "content": content,
            "timestamp": time.time(),
            "index": len(self.history),
        }
        self.history.append(new_history)
        self.agent_context = agent_context
        if "#####" in content:
            self.orchestration = content.split("#####")[1]
        if len(self.text_context) > 0:
            self.text_context += "\n"
        self.text_context += f"{agent_type}: {content}"
        self.save_history()
        print(f"HISTORY: {self.history}\nAGENT: {self.agent_context}\nTEXT: {self.text_context}\nORCHESTRATION: {self.orchestration}")

class Session:
    def __init__(self, config: Dict[str, Any], session_id: Optional[str] = None):
        """
        Initialize the session
        """
        self.history = History(config["version"], session_id)
        self.version: str = "0.0.1" # TODO LOAD THIS FROM SOME OTHER PLACE (toml)
        self.start_time: float = time.time()
        settings: Dict[str, Any] = config["settings"]
        self.orchestrator: OrchestratorAgent = OrchestratorAgent(settings["orchestrator_model"], config)
        
        # load with history if session_id is provided
        if session_id:
            self.orchestrator = OrchestratorAgent(settings["orchestrator_model"], config, self.history.agent_context)
        
        
        self.workflow: WorkflowAgent = WorkflowAgent(settings["workflow_model"], config)

    def gen_orchestration(self, user_input: str) -> str:
        """
        Orchestrate the experiment plan.
        """
        response: str = self.orchestrator.call(user_input)
        self.history.add_history("orchestrator", "orchestration", response, self.orchestrator.dialog_history)
        return response
    
    def complete_orchestration(self) -> None:
        """
        Mark the orchestration step as complete for the session
        """
        self.history.status["orchestration"] = True

    def gen_code(self, content: str) -> None:
        """
        Generate code (for the app, YAMLs, etc.)
        """
        # TODO - kick off the code generation loop
        # TODO - to start just do code gen without validation
        pass

    def gen_workflow(self, user_input = "") -> None:
        """
        Generate workflow yaml.
        """
        response: str = self.workflow.gen_workflow(user_input)
        self.history.add_history("workflow", "gen_workflow", response, self.workflow.dialog_history)
        return response


    def complete_code(self) -> None:
        """
        Mark the code generation step as complete for the session
        """
        self.history.status["code"] = True

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
