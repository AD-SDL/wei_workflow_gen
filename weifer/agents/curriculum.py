from .labworker import LabWorker
import os, numpy as np
from langchain.chat_models import ChatOpenAI

class CurriculumAgent(LabWorker): 
    def __init__(self, 
                 temperature=0, 
                 model_type="gpt-3.5-turbo", 
                 verbose=True, 
                 sys_template_path=None, 
                 input_template_path=None): 
        super().__init__()
        self.temperature = temperature
        self.model_type = model_type
        self.verbose = verbose
        self.sys_template_path = sys_template_path
        self.input_template_path = input_template_path
        self.llm = ChatOpenAI(temperature=self.temperature, 
                              model_name=self.model_type)


    # def init_chain(self): 
    #     system_template = txtfile_to_string(self.sys_template_path)
    #     input_template = txtfile_to_string(self.input_template_path)
    #     system_message = self.create_system_message(system_template)
    #     input_message = self.create_human_message(input_template)
    #     final_prompt = (system_message + input_message)
    #     chain = LLMChain(llm=self.llm, 
    #                      prompt=final_prompt, 
    #                      verbose=self.verbose)
    #     return chain

    def create_full_plan(): 
        return None
    
    def get_completed_tasks(self):
        return None
    
    def parse_instructions(self): 
        return None
    
    # def parse_robot(self, output_string):
    #     output_start = output_string.find("Robot:")
    #     if output_start == -1:
    #         return None
    #     output_lines = output_string[output_start + len("Robot:"):].strip().split('\n')
    #     parsed_output = "\n".join(output_lines).strip()
    #     return parsed_output

    def parse_robot(self, output_string):
        task_start = output_string.find("Robot:")
        robot_start = output_string.find("Materials:")
        if task_start == -1:
            return None
        task_lines = []
        if robot_start != -1:
            task_lines = output_string[task_start + len("Robot:"):robot_start].strip().split('\n', 1)
        else:
            task_lines = output_string[task_start + len("Robot:"):].strip().split('\n', 1)
        parsed_task = task_lines[0].strip() if task_lines else None
        return parsed_task

    def parse_task(self, output_string):
        task_start = output_string.find("Task:")
        robot_start = output_string.find("Robot:")
        if task_start == -1:
            return None
        task_lines = []
        if robot_start != -1:
            task_lines = output_string[task_start + len("Task:"):robot_start].strip().split('\n', 1)
        else:
            task_lines = output_string[task_start + len("Task:"):].strip().split('\n', 1)
        parsed_task = task_lines[0].strip() if task_lines else None
        return parsed_task
    

    def parse_reasoning(self, output_string):
        task_start = output_string.find("Reasoning:")
        robot_start = output_string.find("Task:")
        if task_start == -1:
            return None
        task_lines = []
        if robot_start != -1:
            task_lines = output_string[task_start + len("Reasoning:"):robot_start].strip().split('\n', 1)
        else:
            task_lines = output_string[task_start + len("Reasoning:"):].strip().split('\n', 1)
        parsed_task = task_lines[0].strip() if task_lines else None
        return parsed_task
    
    def parse_materials(self, output_string):
        output_start = output_string.find("Materials:")
        if output_start == -1:
            return None
        output_lines = output_string[output_start + len("Materials:"):].strip().split('\n')
        parsed_output = "\n".join(output_lines).strip()
        return parsed_output
    

    def add_completed_task() -> np.array: 
        return None

    
    def propose_next_task(self, instructions:str,
                          completed_tasks:str, failed_tasks:str, 
                          ) -> (str, str, str, str): 
        
        final_input = {"instructions":instructions, 
                       "completed_tasks":completed_tasks, 
                       "failed_tasks":failed_tasks}
    
        raw_output = self.chain.run(final_input)

        reasoning = self.parse_reasoning(raw_output)
        next_task = self.parse_task(raw_output)

        if "ot2" in next_task.lower(): 
            robot_token = self.parse_robot(raw_output)
            materials = self.parse_materials(raw_output)
            return (reasoning, next_task, robot_token, materials)
        
        robot_token = self.parse_robot(raw_output)
        materials = ""
        return (reasoning, next_task, robot_token, materials)
    

if __name__ == "__main__": 
    os.environ["OPENAI_API_KEY"] = "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"
    curragent = CurriculumAgent()
    chain = curragent.init_chain()

    instructions = "Run PCR with 3 thermocycling cycles and seal plate for 20 minutes at 175 celsius"
    completed_tasks = "None"
    failed_tasks = "None"

    task, robot_token = curragent.propose_next_task(chain=chain, 
                                                    instructions=instructions, 
                                                    completed_tasks=completed_tasks, 
                                                    failed_tasks=failed_tasks)
    
    print(task, robot_token)
