from agents import (LabWorker, ActionAgent, CriticAgent, CurriculumAgent, ToolsAgent, MappingAgent)
from env import Environment
import os, openai, argparse
from utils.parser_utils import *
from utils.general_utils import *


def load_api_key(path:str) -> str: 
    api_key = txtfile_to_string(path)
    return api_key

class Weifer(LabWorker): 
    def __init__(self, 
                num_tries=5, 
                model_type="gpt-3.5-turbo", 
                raw_yaml = "None", 
                exec_error="None", 
                temperature=0, 
                verbose=True, 
                tool_path=f"{os.getcwd()}/weifer/tool_info/tool_info.csv"
                 ): 
        super().__init__()
        self.num_tries = num_tries
        self.model_type = model_type
        self.temperature = temperature
        self.verbose = verbose
        
        self.tool_path = tool_path
        self.raw_yaml = raw_yaml
        self.exec_error = exec_error

        self.toolsagent = ToolsAgent(model_type=self.model_type, 
                                     temperature=self.temperature,
                                     verbose=self.verbose)
        self.actionagent = ActionAgent(model_type=self.model_type, 
                                       temperature=self.temperature,
                                       verbose=self.verbose)
        self.mappingagent = MappingAgent(model_type=self.model_type,
                                         temperature=self.temperature,
                                         verbose=self.verbose)
        
    def setup_agents(self, tool_path):
        self.actionagent.init_chain("action", "action")
        self.mappingagent.init_chain(agent_type="mapping", template_type="mapping")
        self.tools_df = self.toolsagent.create_tools_df(tool_path) 

    def retrieve_tool(self, token, tools_df): 
        return None

    
    def create_vectorbase(self, ): 
        return None


    def generate_yaml(self, task, 
                     raw_yaml, exec_error, 
                     tool_info, tool_fsl):
        try:
            for i in range(num_tries): 
                output = self.actionagent.generate(task=task, raw_yaml=raw_yaml, 
                                            tool=token, exec_error=exec_error,
                                            tool_info=tool_info, tool_demo=tool_fsl)     
                if type(output["result"]) == dict: 
                    break
                exec_error = output["result"]
                raw_yaml = output["raw_yaml"]
            assert type(output["result"])==dict, f"Generating process failed for your task on the {i}th try, here is my best try: {output['raw_output']}"
            return output["result"]
        except Exception as e: 
            error = e 
            return f"Error parsing yaml output (before program execution):\n{error}"
        

    def generate_wei(self, task:str) -> dict: 

        return None 



if __name__=="__main__": 

    parser = argparse.ArgumentParser(description="Wei Generation From Natural Language")

    parser.add_argument('--api_key_path', default='/Users/BrianHsu/Desktop/GitHub/openai_api_key_mine.txt', type=str)
    parser.add_argument('--tool_path', default=f"{os.getcwd()}/weifer/tool_info/tool_info.csv", type=str)
    args = parser.parse_args()

    api_key = load_api_key(args.api_key_path)

    os.environ["OPENAI_API_KEY"] = api_key 
    openai.api_key = api_key

    toolsagent = ToolsAgent()
    actionagent = ActionAgent()
    mappingagent = MappingAgent()

    actionagent.init_chain("action", "action")
    mappingagent.init_chain(agent_type="mapping", template_type="mapping")
    tools_df = toolsagent.create_tools_df(args.tool_path)


    task = "use pf400 to move plate from sciclops to ot2"
    token = mappingagent.map_task(task=task)
    tool_info = toolsagent.query_tool_info(token=token, df=tools_df)
    tool_fsl = toolsagent.query_tool_fsl(token=token, df=tools_df)
    
    num_tries = 5
    raw_yaml = "None"
    exec_error="None"
    lab_state={"task":task, 
            "raw_yaml":raw_yaml, 
            "exec_error":exec_error, 
            "tool_fsl":tool_fsl, 
            "tool_info":tool_info}


    def generate_wei(task, raw_yaml, 
                     exec_error, tool_info, 
                     tool_fsl):
        try:
            for i in range(num_tries): 
                output = actionagent.generate(task=task, raw_yaml=raw_yaml, 
                                                        tool=token, exec_error=exec_error,
                                                        tool_info=tool_info, tool_demo=tool_fsl)     
                if type(output["result"]) == dict: 
                    break
                exec_error = output["result"]
                raw_yaml = output["raw_yaml"]
            assert type(output["result"])==dict, f"Generating process failed for your task on the {i}th try, here is my best try: {output['raw_output']}"
            return output["result"]
        except Exception as e: 
            error = e 
            return f"Error parsing yaml output (before program execution):\n{error}"

    result = generate_wei(**lab_state)


    



    print(instructions)


