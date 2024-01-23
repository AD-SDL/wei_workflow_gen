from .labworker import LabWorker
from langchain.chat_models import ChatOpenAI


class CriticAgent(LabWorker): 
    def __init__(self, 
                 success=False, 
                 temperature=0, 
                 model_type="gpt-3.5-turbo", 
                 verbose=True, 
                 sys_path="./Prompts/critic_prompts/critic.txt", 
                 input_template="./Prompts/Templates/critic_template.txt"): 
        super().__init__()

        self.success=success
        self.temperature = temperature
        self.model_type=model_type
        self.verbose = verbose
        self.llm = ChatOpenAI(temperature=self.temperature, 
                              model_name=self.model_type)
        self.sys_path = sys_path
        self.input_template = input_template
        
    def check_exec(self, exec_error):
        if "none" in exec_error.lower(): 
            self.success==True
        return self.success
    
    def parse_critique(self, input_string):
        critique_start = input_string.find("Critique:")
        success_start = input_string.find("Success:")
        if critique_start == -1 or success_start == -1:
            return None
        critique_lines = input_string[critique_start + len("Critique:"):success_start].strip()
        return critique_lines
    
    def parse_success(self, output_string):
        output_start = output_string.find("Success:")
        if output_start == -1:
            return None
        output_lines = output_string[output_start + len("Success:"):].strip().split('\n')
        parsed_output = "\n".join(output_lines).strip()
        return parsed_output
    
    def check_gpt(self, raw_output:str, 
                  task:str, tool_info:str) -> (str, bool):
        final_input = {"tool_info": tool_info, 
                       "task": task, 
                       "raw_output": raw_output}
        raw_critique = self.chain.run(final_input)
        critique = self.parse_critique(raw_critique)
        pass_critique = eval(self.parse_success(raw_critique))
        return {"critique":critique, 
                "success":pass_critique}
    
    # TODO: either change the prompts or make it so that there is an alternate gpt 
    # that can critique it 
    
    def check_task_success(self, raw_yaml:str, 
                           task:str, tool_info:str, 
                           exec_error:str) -> (str, bool): 
        """First, check if it there are execution errors aka if exec_errors=None. If None, success=True, and we continue.
        If exec_errors has something, success=False, and then we exit early with critique='None'"""
        assessment = self.check_gpt(raw_output=raw_yaml, task=task, tool_info=tool_info)
        self.success = assessment["success"]
        self.success = self.check_exec(exec_error=exec_error)
        return {"critique":assessment["critique"], 
                "success":self.success}
    
