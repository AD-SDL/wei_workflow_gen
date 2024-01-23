from .labworker import LabWorker

import pandas as pd, numpy as np
# from explorer.agents.labworker import LabWorker
from utils.general_utils import (embed_text)
import oyaml as yaml, re
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from sklearn.metrics.pairwise import cosine_similarity


class ToolsAgent(LabWorker): 
    def __init__(self, 
                 temperature=0, 
                 model_type="gpt-3.5-turbo", 
                 verbose=True): 
        super().__init__()
        self.temperature = temperature
        self.model_type = model_type
        self.verbose = verbose

        self.llm = ChatOpenAI(temperature=self.temperature, 
                              model_name=self.model_type)


    def create_workflow_df(self, yaml_path:str) -> pd.DataFrame: 
        with open(yaml_path, 'r') as file: 
            configuration = yaml.safe_load(file)
        modules_list = configuration["flowdef"]
        df = pd.DataFrame(columns=["text", "workflow_module"])
        for i,_ in enumerate(modules_list): 
            description = modules_list[i]["name"]
            module = modules_list[i]
            new_data = [{"text": description, "workflow_module": module}]
            new_df = pd.DataFrame(new_data, columns = ["text", "workflow_module"]) 
            new_df["embedding"] = new_df["text"].apply(embed_text)
            df = pd.concat([df, new_df], ignore_index=True)
        return df

    def create_tools_df(self, csv_path:str) -> pd.DataFrame: 
            tools_df = pd.read_csv(csv_path)
            tools_df["Embedded Tool Name"] = tools_df["Tool Name"].apply(embed_text)
            return tools_df

    def step_to_array(self, GPT_output): 
        numbered_instructions = re.findall(r'\d+\..*$', GPT_output, flags=re.MULTILINE)
        array_instructions = np.array(numbered_instructions)
        return array_instructions
    
    def string_to_array(self, string): 
         array = np.array(string)
         return array

    def plan_query_tool_df(self, array_instruct: np.array, array_idx: int,df: pd.DataFrame) -> dict: 
        query = embed_text(array_instruct[array_idx])
        df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity([x], [query])[0][0])
        max_similarity_index = df['similarity'].idxmax()
        prompt = df.loc[max_similarity_index, "Prompt"]
        return prompt
    
    def query_tool_info(self, token:str, df: pd.DataFrame) -> dict: 
        query = embed_text(token)
        df['similarity'] = df['Embedded Tool Name'].apply(lambda x: cosine_similarity([x], [query])[0][0])
        max_similarity_index = df['similarity'].idxmax()
        prompt = df.loc[max_similarity_index, "Prompt"]
        return prompt
    
    def query_tool_fsl(self, token:str, df: pd.DataFrame) -> dict: 
        query = embed_text(token)
        df['similarity'] = df['Embedded Tool Name'].apply(lambda x: cosine_similarity([x], [query])[0][0])
        max_similarity_index = df['similarity'].idxmax()
        prompt = df.loc[max_similarity_index, "Demo"]
        return prompt

