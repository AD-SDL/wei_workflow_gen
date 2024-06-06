import unittest
from .gen_env import WorkflowGen, CodeGen, ConfigGen

class TestGenEnv(unittest.TestCase):
    def setUp(self):
        # Setup the test environment
        config = {
            "api_keys": {
                "openai": {
                    "key": "sk-",
                    "org": "org-"
                }
            },
            "settings": {
                "framework_model": "gpt-4-turbo",
                "code_model": "gpt-4-turbo",
                "validator_model": "gpt-4-turbo",
                "workflow_model": "gpt-4-turbo",
                "critic_model": "gpt-4-turbo",
                "config_model": "gpt-4-turbo"
            }
        }
        self.workflow_gen = WorkflowGen(config)
        self.code_gen = CodeGen(config)
        self.config_gen = ConfigGen(config, "ot2")

    def test_code_gen(self):
        # Test if PCR workflows are retrieved from a super basic query
        workflow = self.workflow_gen.generate_code("PCR Experiment")
        print("Generated workflow:", workflow)
        results = self.code_gen.generate_code("PCR Experiment", workflow)
        print("Generated workflow code:", results)

        # test config
        config = self.config_gen.generate_code("PCR Experiment", )
        print("Generated workflow code:", config,)


if __name__ == '__main__':
    unittest.main()