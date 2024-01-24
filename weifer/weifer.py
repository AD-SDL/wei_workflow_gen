from agents import (LabWorker, ActionAgent, CriticAgent, CurriculumAgent, ToolsAgent)
from env import Environment
import os, openai, argparse
from utils.parser_utils import *
from utils.general_utils import *


class weifer(LabWorker): 
    def __init__(self, ): 
        super().__init__()
    


if __name__=="__main__": 

    parser = argparse.ArgumentParser(description="Wei Generation From Natural Language")

    parser.add_argument('--openai_api_key', default='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', type=str)
    parser.add_argument('--tool_path', default=f"{os.getcwd()}/tool_info/tool_info.csv", type=str)
    args = parser.parse_args()

    os.environ["OPENAI_API_KEY"] = args.openai_api_key
    openai.api_key = args.openai_api_key

    toolsagent = ToolsAgent()
    actionagent = ActionAgent()
    mappingagent = 

    tools_df = toolsagent.create_tools_df(args.tool_path)


    



    print(instructions)


