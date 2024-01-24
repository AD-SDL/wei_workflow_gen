import re, numpy as np, openai, os
import oyaml as yaml, pandas as pd
from sklearn.metrics.pairwise import cosine_similarity





def load_instructions(type:str) -> str: 
    """Get input instruction prompts for agent inference"""
    auto_path = os.getcwd()
    file_path = f"{auto_path}/test_inputs/instructions/{type}.txt"
    with open(file_path, "r") as file: 
        prompt_string = file.read() 
    return prompt_string

def load_agent_prompt(agent:str) -> str:
    """Gets agent system prompts as a str by using getcwd()
    Choose: 
    - action
    - actionot2
    - critic
    - curriculum
    """
    auto_path = os.getcwd()
    file_path = f"{auto_path}/explorer/prompts/{agent}.txt"
    with open(file_path, "r") as file: 
        prompt_string = file.read() 
    return prompt_string

def load_template(agent:str) -> str: 
    """Gets template prompts as a str by using getcwd()"""
    auto_path = os.getcwd()
    file_path = f"{auto_path}/explorer/templates/{agent}_template.txt"
    with open(file_path, "r") as file: 
        prompt_string = file.read() 
    return prompt_string

def load_test_output(test:str, status:str) -> str: 
    """Gets test processed_output as an str by using getcwd() for testing parsing functions"""
    auto_path = os.getcwd()
    file_path = f"{auto_path}/explorer/test_inputs/{status}/{test}.txt"
    with open(file_path, "r") as file: 
        processed_string = file.read() 
    return processed_string

def txtfile_to_string(file_path:str) -> str: 
    """Use to turn a text file into a string
    Parameters 
    ==========
    file_path: str
        file_path to txt file as a string 
    Output
    =========
    prompt_string: str
        contents of txt file as a string
    """
    with open(file_path, "r") as file: 
        prompt_string = file.read()
    return prompt_string


# NOTE: this might require ver openai 0.0.028
def embed_text(text:str) -> np.array: 
    """Function that returns embedding vector for a string 
    Parameters
    ==========
    text: str
        string that you want to embed 
    embedding_model: str
        embedding model type from openai
    Output 
    =========
    vector: np.array
        vector embedding of string
    """
    embedding_object = openai.Embedding.create(input = text, model="text-embedding-ada-002")
    vector = np.array(embedding_object.data[0].embedding)
    return vector

def create_workflow_df(yaml_path:str) -> pd.DataFrame: 
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

def create_tools_df(tools_df: pd.DataFrame) -> pd.DataFrame: 
        tools_df["embedding"] = tools_df["Tool Name"].apply(embed_text)
        return tools_df

def string_to_array(GPT_output): 
    numbered_instructions = re.findall(r'\d+\..*$', GPT_output, flags=re.MULTILINE)
    array_instructions = np.array(numbered_instructions)
    return array_instructions

def query_tool_df(array_instruct: np.array, array_idx: int,df: pd.DataFrame) -> dict: 
    query = embed_text(array_instruct[array_idx])
    df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity([x], [query])[0][0])
    max_similarity_index = df['similarity'].idxmax()
    prompt = df.loc[max_similarity_index, "Prompt"]
    return prompt

def query_df(mapping_array: np.array, array_idx: int,df: pd.DataFrame) -> dict: 
    query = embed_text(mapping_array[array_idx])
    df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity([x], [query])[0][0])
    # Get the index of the row with maximum similarity
    max_similarity_index = df['similarity'].idxmax()
    # Retrieve the 'workflow_module' dictionary from the DataFrame
    prompt = df.loc[max_similarity_index, "Prompt"]
    return prompt

def add_metadata(composed_yaml: list) -> dict:
    flowdef = {"flowdef": composed_yaml}
    modules_list = []
    for i in range(len(flowdef["flowdef"])):
        module_name = flowdef["flowdef"][i]["module"]
        if module_name in modules_list:
            pass 
        else: 
            modules_list.append(module_name)
        modules = [{"name": module_name} for module_name in modules_list]
        modules_dict = {"modules":modules}
    modules_dict
    name_dict = {"name": "PCR Workflow"}
    metadata_dict = {"metadata": {"author": "RPL Team", 
                                "info": "whatever", 
                                "version": "0.1"}}
    workflow = name_dict | metadata_dict | modules_dict | flowdef
    return workflow


def save_workflow(output_file_path: str, workflow:dict) -> None:
    with open(output_file_path, 'w') as file:
        yaml.dump(workflow, file, default_flow_style=False)
    return f"workflow yaml saved in {output_file_path}"