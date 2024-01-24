from .labworker import LabWorker
import oyaml as yaml
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from utils.parser_utils import (parse_sealer, parse_sciclops, 
                                parse_pf400, parse_biometra, 
                                parse_peeler, parse_ot2, preprocess_raw_output)
from utils.general_utils import (txtfile_to_string, load_instructions)

class ActionAgent(LabWorker): 
    def __init__(self, 
                 temperature=0, 
                 model_type="gpt-3.5-turbo", 
                 verbose=True, 
                 agent_type="action", 
                 template_type="action"):
        super().__init__()
        self.temperature = temperature
        self.model_type = model_type
        self.verbose = verbose
        self.llm = ChatOpenAI(temperature=self.temperature, 
                            model_name=self.model_type)
        self.agent_type=agent_type
        self.template_type=template_type
        
    
    def generate_raw(self, task:str, raw_yaml:str,
                      exec_error:str,
                      tool_info:str, tool_demo:str
                      ) -> yaml: 
        """Takes in previous round info + task + tool info + tool fsl --> return raw str (non_ot2)
        Must be ran on a unique chain/agent"""
        final_input = {"tool_info": tool_info, 
                       "tool_demo": tool_demo,
                       "task": task, 
                       "raw_yaml": raw_yaml, 
                       "exec_error": exec_error}
        raw_output = self.chain.run(final_input)
        return raw_output

    def generate_raw_ot2(self, task:str, raw_yaml:str, 
                          exec_error:str): 
        """Takes in previous round info + task + tool info + tool fsl --> return raw str (non_ot2)
        Must be ran on a unique chain/agent"""
        final_input = {"task": task, 
                       "raw_yaml": raw_yaml, 
                       "exec_error": exec_error} 
        raw_output = self.ot2chain.run(final_input)
        return raw_output
    
    def priyanka_reaction(self, instruct_path:str) -> str: 
        instructions = txtfile_to_string(instruct_path)
        return instructions
    
    def parse_output(self, raw_yaml:str, tool_name:str) -> (dict, str): 
        """This function takes in the raw output string from the create_raw_yaml() function and parses it to convert it into a dictionary
        Parameters
        ==========
        raw_output: str
            This is the raw output string from GPT that contains the workcell tool information
        tool_name: str
            This is the name of the tool that you are using to parse the tool 
        Output
        ==========
        yaml_dict: dict
            This is a dictionary format of the tool use output that GPT uses 
        """ 
        # if run into tool, use specific parsing func
        if "sciclops" in tool_name.lower(): 
            result = parse_sciclops(raw_yaml)
        elif "biometra" in tool_name.lower(): 
            result = parse_biometra(raw_yaml)
        elif "peeler" in tool_name.lower(): 
            result = parse_peeler(raw_yaml)
        elif "ot2" in tool_name.lower(): 
            result = parse_ot2(raw_yaml)
        elif "pf400" in tool_name.lower(): 
            result = parse_pf400(raw_yaml)
        elif "sealer" in tool_name.lower(): 
            result = parse_sealer(raw_yaml)
        return result
    
    # TODO: GIVE WELL LOCATIONS AND SEE IF IT CAN GENERATE THE PROPER LOCATIONS AND DESTINATIONS
    def pcr_policy_sample(self, task:str, 
                   raw_yaml:str, tool:str, 
                   exec_error:str,
                   tool_info:str, tool_demo:str, 
                   ): 
        """takes in tool info:str and task:str and returns a dict{code} if successful or str:error if unsuccessful parsing
        if ot2, loads numbered instructions from: '{auto_path}/explorer/test_inputs/instructions/{type}.txt'"""
        if "ot2" in tool.lower():
            # TODO: this function will send the materials var str to priyanka, and recieve the instruction
            # steps to run the experiment
            instructions = load_instructions(type="ot2")
            raw_output = self.generate_raw_ot2(task=instructions, raw_yaml=raw_yaml, 
                                            exec_error=exec_error)
            raw_yaml = preprocess_raw_output(raw_output)
            result = self.parse_output(raw_yaml=raw_yaml, tool_name=tool)
            return {"result":result, 
                    "raw_yaml":raw_yaml}
        
        raw_output = self.generate_raw(task=task, raw_yaml=raw_yaml, exec_error=exec_error, 
                                       tool_info=tool_info, tool_demo=tool_demo)
        raw_yaml = preprocess_raw_output(raw_output)
        # TODO: change all the raw_output to raw_yaml in the parsers
        # dict if correct, str if not 
        result = self.parse_output(raw_yaml, tool)
        return {"result":result, 
                "raw_yaml":raw_yaml, 
                "raw_output":raw_output}

