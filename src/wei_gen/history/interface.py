import uuid
import os
import json
import time
from typing import Optional, Dict, List, Any

class History:
    def __init__(self, version: str, session_id: Optional[str] = None, dir = "../../history"):
        """
        Initialize the history of the session
        """
        self.session_id: str = session_id if session_id else str(uuid.uuid4())
        print("passed", session_id, "using", self.session_id)
        starting_time = time.time()
        # Define the path to the JSON file 
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.history_file_path: str = f"{base_dir}/{dir}/{self.session_id}.json"
        

        if session_id: # If there's a session_id, try to load the existing history
            loaded_data: Dict[str, Any] = self._load_history()
            self.v: Dict[str, Any] = loaded_data
        else:
            self.v: Dict[str, Any] = {
                "version": version,
                "session_id":  self.session_id,
                "timestamp": starting_time,
                "validity": 0,

                "original_user_description": "",
                "original_user_values": "",

                "framework_agent_ctx": None,
                "workflow_agent_ctx": None,
                "code_agent_ctx": None,
                "validator_agent_ctx": None,
                "config_agent_ctx": None,
               

                "generated_framework": "",
                "generated_code": "",
                "generated_workflow": "",
                "generated_config": "",
            }

    def _load_history(self) -> Dict[str, Any]:
        """
        Load history from a JSON file
        """
        try:
            with open(self.history_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: {self.history_file_path} not found.")
            return {}

    def _save_history(self) -> None:
        """
        Save the current history to a JSON file
        """
        with open(self.history_file_path, 'w') as file:
            json.dump(self.v, file, indent=4)

    def add_agent_history(self, agent_type: str, agent_context: List[Any], generated_content = None) -> None:
        """
        Add a new entry to the session
        """
        self.v[f"{agent_type}_agent_ctx"] = agent_context
        if generated_content:
            self.v[f"generated_{agent_type}"] = generated_content
        self._save_history()
    

    def set_user_inputs(self,user_description, user_values) -> None:
        self.v["original_user_description"] = user_description
        self.v["original_user_values"] = user_values
        self._save_history()


    def update_generated(self, agent_type: str, generated_content: Any) -> None:
        self.v[f"generated_{agent_type}"] = generated_content
        self._save_history()

    def get_generated(self, agent_type: str):
        return self.v[f"generated_{agent_type}"]
    


    def get_user_values(self):
        print("original_user_values", self.v["original_user_values"],self.v)
        return self.v["original_user_values"]

