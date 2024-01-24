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
                 agent_type="action", 
                 template_type="action"): 
        super().__init__()
        
        self.temperature=temperature
        self.model_type=model_type
        self.verbose=verbose
        self.agent_type=agent_type
        self.template_type=template_type


    def lod
