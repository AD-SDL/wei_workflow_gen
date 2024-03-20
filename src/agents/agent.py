from wrapper import *
# from prompts import seller_gen
# from prompts import buyer_gen
from copy import deepcopy
from openai import OpenAI

class Agent:
    def __init__(self, agent_type, model, config, item, initial_prompt):
        self.agent_type = agent_type
        self.model = model # The model name
        self.initial_dialog_history = deepcopy(initial_prompt)
        self.config = config
        self.item = item # TODO remove this from args
        self.dialog_history = [] if len(initial_prompt) == 0 else deepcopy(initial_prompt)
        self._initialize_engine()
        


    def _initialize_engine(self):
        print("Initializing", self.agent_type,"engine", self.model)
        # Initialize specific API clients based on the engine type
        if "cohere" in self.model:
            self.engine = cohere.Client(self.config["api_keys"]["cohere"]["key"])
        elif "gpt" in self.model:
            self.engine = OpenAI(api_key=self.config["api_keys"]["openai"]["key"], organization=self.config["api_keys"]["openai"]["org"])
        elif "phi-2" in self.model:
            self.engine = self.config["open_source_urls"]["phi-2"]
        elif "gemini" in self.model:
            genai.configure(api_key=self.config["api_keys"]["gemini"]["key"])
            self.engine = genai.GenerativeModel(self.model)
        elif "mixtral" in self.model:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.config["api_keys"]["mistral"]["key"]}'
            }
            self.engine = headers
        elif "llama" in self.model:
            self.engine = self.config["llama_engine"]


    
    def reset(self):
        """Reset dialog history"""
        self.dialog_history = deepcopy(self.initial_dialog_history)
        return 
    
    def _parse_response(self, engine, response):
        """Parse response based on engine type."""
        if engine == "gpt-3.5-turbo" or "gpt-3.5" in engine:
            return response.choices[0].message.content
        elif engine == "gpt-4":
            return response.choices[0].message.content
        elif engine == "llama":
            res = response[0]["generation"]["content"]
            print("llama response", res)
            return str(res)
        else:
            raise ValueError(f"Unknown engine {engine}")

    def call_engine(self, messages, raw = False):
        """Route the call to different engines"""
        model_handlers = {
            "gpt-3.5-turbo": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
            "gpt-3.5-turbo-0125": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
            "gpt-4": lambda: openai_completion_with_backoff(engine=self.engine, model=self.model, messages=messages),
        }
        

        if self.model in model_handlers:
            response = model_handlers[self.model]()
            if raw:
                return response
            return self._parse_response(self.model, response)
        else:
            raise ValueError(f"Unknown model {self.model}")
    
    def call(self, prompt):
        if prompt:
            prompt = {"role": "user", "content": prompt}
            self.dialog_history.append(prompt)
            self.last_prompt = prompt['content']
        messages = list(self.dialog_history)
        message = self.call_engine(messages)
        store = {"role": "assistant", "content": message}
        self.dialog_history.append(store)
        return message

    def last_response(self):
        return self.dialog_history[-1]['content']
    
    def add_advice(self, content):
        new_message = {"role": "system", "content": content}
        self.dialog_history.append(new_message)



class OrchestrationAgent(Agent):
    # TODO: Implement this class
    pass

class CodeAgent(Agent):
    # TODO: Implement this class
    pass


class ValidatorAgent(Agent):
    # TODO: Implement this class
    pass