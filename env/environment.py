

class Environment(): 
    def __init__(self, 
                 error_list=[]): 
        self.tool_list = ["sciclops", "biometra", "sealer", "peeler", "ot2", "pf400"]
        self.error_list = error_list
    
    # TODO: get rid of this; agent already does this 
    # def parse_yaml(self, raw_output:str, tool:str) -> (str, str):
    #     """This function validates the raw output and returns a bool"""
    #     raw_output = preprocess_raw_output(raw_output)
    #     yaml_code, error_message = raw_to_dict(raw_output, tool)
    #     return (yaml_code, error_message)

    def exec_yaml_format(self, yaml_code:str, tool:str) -> (str, str): 
        """This will use Ryan/My RestAPI functions to validate the yalm format
        For now, just return no error for any of them"""
        error = "None"
        return error
    
    def omniverse_state(self, yaml_code:str, tool:str) -> (str, str): 
        """Rory's output from omniverse"""
        lab_state = ""
        return lab_state    
    
    def reset(self): 
        self.error_list=[]
        return None
    
    # todo: create yaml tool that unpacks the yaml dict into a yaml string and appends the string 
    # under the args section of the pre-made ot2 yaml
    

    def step(self, yaml_code:dict, tool:str) -> dict: 
        """Take in code dict and tool info, then:
        1.) Runs it through Ryan's yaml function to see if the yaml argument inputs match the abouts
        2.) Runs it through Rory's omniverse to get the lab envionment state
        
        returns dict{error:str, lab_state:str}
        """
        if "ot2" in tool.lower():
            return None
        
        error = self.exec_yaml_format(yaml_code=yaml_code, tool=tool)
        lab_state = self.omniverse_state(yaml_code=yaml_code, tool=tool)
        return {"error":error, 
                "lab_state":lab_state}
