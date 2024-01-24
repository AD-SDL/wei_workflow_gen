# Importing all necessary packages 
from langchain.prompts import (FewShotChatMessagePromptTemplate, 
                               HumanMessagePromptTemplate, AIMessagePromptTemplate, 
                               SystemMessagePromptTemplate)
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.prompts.chat import MessagesPlaceholder
import json
from langchain.chat_models import ChatOpenAI
from utils.general_utils import (load_agent_prompt, load_template) 

class LabWorker(): 
    def __init__(self, temperature=0, model_type="gpt-3.5-turbo", verbose=True):
        
        self.temperature = temperature
        self.model_type = model_type
        self.verbose = verbose

    def init_chain(self, agent_type:str, template_type:str) -> LLMChain: 
        """Initialized LLMChain based on agent_type [action, critic, curriculum]
        and template_type [action, critic, curriculum, actionot2]"""
        system_template = load_agent_prompt(agent_type)
        input_template = load_template(template_type)
        system_message = self.create_system_message(system_template)
        human_message = self.create_human_message(input_template)
        final_prompt = (system_message + human_message)
        self.chain = LLMChain(llm = self.llm, 
                         prompt = final_prompt, 
                         verbose = self.verbose)
        return self.chain
    
    def init_ot2chain(self, agent_type:str, template_type:str) -> LLMChain: 
        """Initialized ot2 LLMChain based on agent_type [action, critic, curriculum]
        and template_type [action, critic, curriculum, actionot2]"""
        system_template = load_agent_prompt(agent_type)
        input_template = load_template(template_type)
        system_message = self.create_system_message(system_template)
        human_message = self.create_human_message(input_template)
        final_prompt = (system_message + human_message)
        self.ot2chain = LLMChain(llm = self.llm, 
                         prompt = final_prompt, 
                         verbose = self.verbose)
        return self.ot2chain

    def grab_few_shot(self, example_name: str, few_shot_path:str) -> str: 
        with open(few_shot_path, "r") as file: 
            self.few_shot_examples = json.load(file)
        example_direction = self.few_shot_examples[example_name][0]
        example_code = self.few_shot_examples[example_name][1]
        example = [example_direction, example_code]
        return example
    
    def create_few_shot_message(self, example_one:list, example_two:list) -> str:
        examples = [{"input": example_one[0], "output": example_one[1]}, 
            {"input": example_two[0], "output": example_two[1]}]
        example_prompts = (
            HumanMessagePromptTemplate.from_template("{input}")
            + AIMessagePromptTemplate.from_template("{output}")
            )
        few_shot_message = FewShotChatMessagePromptTemplate(
        examples = examples, 
        example_prompt = example_prompts
        )
        return few_shot_message
    
    def create_system_message(self, system_template: str) -> str:
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        return system_message
    
    def create_human_message(self, human_template:str) -> str: 
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        return human_message
    
    def create_prompt(self, system_template:str, human_template:str) -> str: 
        system_prompt = self.create_system_message(system_template)
        human_prompt = self.create_human_message(human_template)
        final_prompt = (system_prompt + human_prompt)
        return final_prompt

    def basic_message_str(human_message:str, system_message:str) -> str: 
        return None
    
    def create_memory(self) -> list:
        history_message = MessagesPlaceholder(variable_name="chat_history")
        memory_gen = ConversationBufferWindowMemory(k=10, memory_key = "chat_history", return_messages = True)
        memory = [history_message, memory_gen]
        return memory
    
    def view_prompt(self, few_shot_message:str, system_message:str, 
                    human_message:str) -> str: 
        final_prompt = (
            system_message
            + few_shot_message
            + human_message
        )
        print(final_prompt.format(input_prompt = "\n/*input_prompt goes here*/\n"))

    def create_final_prompt(self, few_shot_message:str, system_message:str, 
                            human_message:str, memory:list, use_memory:bool) -> str:
        if use_memory == True:
            final_prompt = (
            system_message 
            + few_shot_message
            + memory[0]
            + human_message
        )
        else:
            final_prompt = (
                system_message 
                + few_shot_message
                + human_message
            )
            
        return final_prompt

    def auto_make_prompt(self, 
                        few_shot_path:str, 
                        system_template_path:str, 
                        human_template_path:str, 
                        use_memory:bool) -> str:

        # compile few_shot_message
        example_one = self.grab_few_shot(example_name="example_one", few_shot_path=few_shot_path)
        example_two = self.grab_few_shot(example_name="example_two", few_shot_path=few_shot_path)
        few_shot_message = self.create_few_shot_message(example_one=example_one, 
                                                        example_two=example_two)
        # create system_message
        system_template = txtfile_to_string(system_template_path)
        system_message = self.create_system_message(system_template=system_template)
        # create human_message
        human_template = txtfile_to_string(human_template_path)
        human_message = self.create_human_message(human_template=human_template)
        # create memory 
        memory = self.create_memory()

        if use_memory == True:
            # create final prompt 
            final_prompt = self.create_final_prompt(few_shot_message=few_shot_message, 
                                                        system_message=system_message, 
                                                        human_message=human_message, 
                                                        memory=memory, 
                                                        use_memory=True)
            return final_prompt, memory
        
        else: 
            # create final prompt 
            final_prompt = self.create_final_prompt(few_shot_message=few_shot_message, 
                                                        system_message=system_message, 
                                                        human_message=human_message,
                                                        memory=memory, 
                                                        use_memory=False)
            return final_prompt
    

    # TODO: refine this method so that it appends it as one string 
    # rather than a one off list
    def get_chat_history(self, chain:LLMChain) -> str:
        chat_input=chain.memory.chat_memory.messages[0].content
        chat_output=chain.memory.chat_memory.messages[1].content
        chat_history = [chat_input, chat_output]
        return chat_history
    

    def create_basic_chain(self, final_prompt:str) -> LLMChain:
        # temperature inherited from labworker  
        llm = ChatOpenAI(temperature=self.temperature, 
                         model_name=self.model_type)
        basic_chain = LLMChain(llm = llm, 
                        prompt = final_prompt, 
                        verbose = self.verbose)
        return basic_chain
