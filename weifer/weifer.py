from agents import (LabWorker, ActionAgent, CriticAgent, CurriculumAgent, ToolsAgent, MappingAgent)
from env import Environment
import os, openai, argparse
from utils.parser_utils import *
from utils.general_utils import *


def load_api_key(path:str) -> str: 
    api_key = txtfile_to_string(path)
    return api_key

class Weifer(LabWorker): 
    def __init__(self, ): 
        super().__init__()
    


if __name__=="__main__": 

    parser = argparse.ArgumentParser(description="Wei Generation From Natural Language")

    parser.add_argument('--api_key_path', default='/Users/BrianHsu/Desktop/GitHub/openai_api_key_mine.txt', type=str)
    parser.add_argument('--tool_path', default=f"{os.getcwd()}/weifer/tool_info/tool_info.csv", type=str)
    args = parser.parse_args()

    api_key = load_api_key(args.api_key_path)

    os.environ["OPENAI_API_KEY"] = api_key 
    openai.api_key = api_key

    num_tries = 5
    task = "use pf400 to move plate from sciclops to ot2"

    toolsagent = ToolsAgent()
    actionagent = ActionAgent()
    mappingagent = MappingAgent()

    actionagent.init_chain("action", "action")
    mappingagent.init_chain(agent_type="mapping", template_type="mapping")
    tools_df = toolsagent.create_tools_df(args.tool_path)
    token = mappingagent.map_task(task=task)

    tool_info = toolsagent.query_tool_info(token=token, df=tools_df)
    tool_fsl = toolsagent.query_tool_fsl(token=token, df=tools_df)
    for i in range(num_tries): 
        # proposing the next task 
        output = actionagent.generate(task=task, raw_yaml=raw_yaml, 
                                                tool=token, exec_error=exec_error,
                                                tool_info=tool_info, tool_demo=tool_fsl)     
        # if parsing fails, then update exec_error, and yaml_code
        if type(output["result"]) == str: 
            exec_error = output["result"]
            raw_yaml = output["raw_yaml"]
            continue


    


    



    print(instructions)


