from agents import (ActionAgent, CriticAgent, CurriculumAgent, ToolsAgent)
from env import Environment
import os, openai, argparse
from utils.parser_utils import *
from utils.general_utils import *

class Explorer(): 
    def __init__(self, test=None): 
        self.test = test



if __name__  == "__main__":

    parser = argparse.ArgumentParser(description="YAML Generation From Natural Language")
    parser.add_argument('--openai_api_key', default=None, type=str)
    parser.add_argument('--model_type', default='gpt-3.5-turbo', type=str)
    parser.add_argument('--verbose', default=True, type=str)
    parser.add_argument('--temperature', default=0, type=int)
    parser.add_argument('--embedding_model', default="text-embedding-ada-002", type=str)
    # instruction files
    parser.add_argument('--csv_tool_path', default=f"{os.getcwd()}/explorer/tool_info/tool_info.csv", type=str)
    args = parser.parse_args()

    os.environ['OPENAI_API_KEY'] = args.openai_api_key
    openai.api_key = args.openai_api_key

    ## Creating agents and their tools
    curragent = CurriculumAgent(model_type="gpt-4")
    toolsagent = ToolsAgent()
    actionagent = ActionAgent()
    criticagent = CriticAgent(model_type="gpt-4")
    lab_env = Environment()
    curragent.init_chain(agent_type="curriculum", template_type="curriculum")
    actionagent.init_chain(agent_type="action", template_type="action")
    actionagent.init_ot2chain(agent_type="actionot2", template_type="actionot2")
    criticagent.init_chain(agent_type="critic", template_type="critic")
    tools_df = toolsagent.create_tools_df(args.csv_tool_path)
    
    instructions = load_instructions("pcr")
    completed_tasks = """sciclops gets plate from stacks
Pf400 transfers plate from sciclops and moves it to ot2_pcr_alpha.deck1_cooler
ot2 performs liquid preparation reaction with materials
pf400 moves plate from ot2 to sealer
sealer seals plate for 20 minutes at 175 C
pf400 moves plate from sealer to biometra 
biometra close plate
biometra run program for 3 times
biometra open lid
pf400 moves plate from biometra to peeler
peeler peel plate
pf400 moves plate to trash"""
    failed_tasks = ""
    end_lab_token = "<END_EXPERIMENT>"
    ot2_token = "ot2"
    composed_yaml = []

    steps = 0
    num_tries = 3
    max_tries = 20
    end_lab=False

    while True:
        if steps >= max_tries:
            print("Max number of lab tries exceeded! Exiting...") 
            break 
        elif end_lab == True: 
            print("Experiment completed! Exiting...")
            break
        raw_yaml = "None"
        exec_error="None"
        critique="None"
        # get the next task information 
        reasoning, task, robot, materials = curragent.propose_next_task(instructions=instructions, 
                                                                        completed_tasks=completed_tasks, 
                                                                        failed_tasks=failed_tasks)
        # terminate the experiment 
        if end_lab_token in robot: 
            end_lab=True
            continue
        # grab tool info and few shot learn 
        tool_info = toolsagent.query_tool_info(token=robot, df=tools_df)
        tool_fsl = toolsagent.query_tool_fsl(token=robot, df=tools_df)
        for i in range(num_tries): 
            # proposing the next task 
            output = actionagent.pcr_policy_sample(task=task, raw_yaml=raw_yaml, 
                                                   tool=robot, exec_error=exec_error, 
                                                   critique=critique, tool_info=tool_info,
                                                   tool_demo=tool_fsl)     
            # if parsing fails, then update exec_error, and yaml_code
            if type(output["result"]) == str: 
                exec_error = output["result"]
                raw_yaml = output["raw_yaml"]
                continue
            env_info = lab_env.step(yaml_code=output["result"], tool=robot)
            assessment = criticagent.check_task_success(raw_yaml=output["raw_yaml"], task=task, 
                                                        tool_info=tool_info, exec_error=env_info["error"]) 
            if assessment["success"]==True: 
                completed_tasks = completed_tasks + "\n" + task + "\n"
                lab_state = env_info["lab_state"]
                print("Testing for SUCCESS")
                break
            # else, update information for another pass
            exec_error = env_info["error"]
            critique = assessment["critique"]
            lab_state = env_info["lab_state"]
            raw_yaml = output["raw_yaml"]
            failed_tasks = task

        if assessment["success"]==True: 
            composed_yaml.append(output["result"])

    print("Experiment Completed! Appending Metadata...")    
        

        
