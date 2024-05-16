import unittest
import os
from .interface import History  # replace 'your_module' with the actual name of your module


class TestHistoryFunctionality(unittest.TestCase):
    
    def setUp(self):
        self.version = "1.0"
        self.history = History(self.version, dir ="test_runs")
        self.history_dir = os.path.dirname(self.history.history_file_path)
        os.makedirs(self.history_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.history.history_file_path):
            os.remove(self.history.history_file_path)
        if os.path.exists(self.history_dir):
            os.rmdir(self.history_dir)

    def test_initialize_new_session(self):
        history = History(self.version)
        self.assertEqual(history.history["version"], self.version)
        self.assertIn("session_id", history.history)
        self.assertIn("timestamp", history.history)
        self.assertIn("framework_agent_ctx", history.history)
        self.assertIn("workflow_agent_ctx", history.history)
        self.assertIn("code_agent_ctx", history.history)
        self.assertIn("validator_agent_ctx", history.history)
        self.assertIn("original_user_input", history.history)
        self.assertIn("generated_framework", history.history)
        self.assertIn("generated_code", history.history)
        self.assertIn("generated_workflow", history.history)
        self.assertIn("generated_config", history.history)
        self.assertIn("status", history.history)

    def test_save_and_load_history(self):
        # Save history
        self.history._save_history()

        # Load history from file
        loaded_history = History(self.version, session_id=self.history.session_id, dir ="test_runs")
        self.assertEqual(loaded_history.history, self.history.history)

    def test_add_agent_history(self):
        agent_context = [{"key": "value"}]
        self.history.add_agent_history("framework", agent_context, "Generated framework content")

        self.assertEqual(self.history.history["framework_agent_ctx"], agent_context)
        self.assertEqual(self.history.history["generated_framework"], "Generated framework content")
        self.assertTrue(self.history.history["status"]["framework"])

    def test_set_validation_status(self):
        self.history.set_validation_status(True)
        self.assertTrue(self.history.history["status"]["validation"])

    def test_set_original_user_input(self):
        user_input = "User input example"
        self.history.set_original_user_input(user_input)
        self.assertEqual(self.history.history["original_user_input"], user_input)

    def test_update_generated_content(self):
        generated_content = "Updated generated content"
        self.history.update_generated_content("code", generated_content)
        self.assertEqual(self.history.history["generated_code"], generated_content)


if __name__ == '__main__':
    unittest.main()
