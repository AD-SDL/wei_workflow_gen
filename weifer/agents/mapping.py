from .labworker import LabWorker
import oyaml as yaml
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from utils.parser_utils import (parse_sealer, parse_sciclops, 
                                parse_pf400, parse_biometra, 
                                parse_peeler, parse_ot2, preprocess_raw_output)
from utils.general_utils import (txtfile_to_string, load_instructions)


class MappingAgent(LabWorker): 
    def __init__(self, 
                 temperature=0, 
                 model_type="gpt-3.5-turbo", 
                 verbose=True, 
                 agent_type="mapping", 
                 template_type="mapping"): 
        super().__init__()
        
        self.temperature=temperature
        self.model_type=model_type
        self.verbose=verbose
        self.agent_type=agent_type
        self.template_type=template_type
        self.llm = ChatOpenAI(temperature=self.temperature, 
                    model_name=self.model_type)
        
    def map_task(self, task:str) -> str: 
        final_input = {"task":task}
        raw_output = self.chain.run(final_input)
        raw_token = preprocess_raw_output(raw_output)
        return raw_token

