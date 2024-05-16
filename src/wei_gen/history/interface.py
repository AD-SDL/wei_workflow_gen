import uuid
import os
import json
import time
from typing import Optional, Dict, List, Any

class History:
    def __init__(self, version: str, session_id: Optional[str] = None, dir = "runs"):
        """
        Initialize the history of the session
        """
        self.session_id: str = session_id if session_id else str(uuid.uuid4())
        
        # Define the path to the JSON file 
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.history_file_path: str = f"{base_dir}/{dir}/{self.session_id}_history.json"

        if session_id: # If there's a session_id, try to load the existing history
            loaded_data: Dict[str, Any] = self._load_history()
            self.history: Dict[str, Any] = loaded_data
        else:
            self.history: Dict[str, Any] = {
                "version": version,
                "session_id": str(uuid.uuid4()),
                "timestamp": time.time(),

                "framework_agent_ctx": [],
                "workflow_agent_ctx": [],
                "code_agent_ctx": [],
                "validator_agent_ctx": [],
                "original_user_input": "",

                "generated_framework": "",
                "generated_code": "",
                "generated_workflow": [],
                "generated_config": [],
                "status": {
                    "validation": False,
                    "framework": False,
                    "workflow": False,
                    "code": False,
                    "config": False,
                },
            }

    def _load_history(self) -> Dict[str, Any]:
        """
        Load history from a JSON file
        """
        try:
            with open(self.history_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Error: File not found.")
            return {}

    def _save_history(self) -> None:
        """
        Save the current history to a JSON file
        """
        with open(self.history_file_path, 'w') as file:
            json.dump(self.history, file, indent=4)

    def add_agent_history(self, agent_type: str, agent_context: List[Any], generated_content = None) -> None:
        """
        Add a new entry to the session
        """
        self.history[f"{agent_type}_agent_ctx"] = agent_context
        if generated_content:
            self.history[f"generated_{agent_type}"] = generated_content
        if self.history["status"][agent_type] == False:
            self.history["status"][agent_type] = True
        self._save_history()
    
    def set_validation_status(self, status: bool) -> None:
        self.history["status"]["validation"] = status
        self._save_history()

    def set_original_user_input(self, user_input: str) -> None:
        self.history["original_user_input"] = user_input
        self._save_history()

    def update_generated_content(self, agent_type: str, generated_content: Any) -> None:
        self.history[f"generated_{agent_type}"] = generated_content
        self._save_history()