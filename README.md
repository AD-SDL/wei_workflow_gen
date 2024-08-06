# wei_gen (v2)
wei_gen is a python package that takes a natural language description of an experiment and generates WEI workflows, code, and instrument configs. wei_gen is packaged as a class, and can be imported into any python project or spun up as an API. Examples of usage are in `/scripts`. An API-ized verion of wei_gen can be found in `/api`.

## Demo
See the demo [here](https://youtu.be/PoWsh9-hheM)

## Frontend
Interact with weigen with a [simple next.js app](https://github.com/nautsimon/wei-gen-client)

## API
The api wrapper of weigen can be found in `/src/api`. The following endpoints are supported.

- /session/init - returns session history on success
- /session/<session_id>/workflow_step - returns session history on success
- /session/<session_id>/code_step - returns session history on success
- /session/<session_id>/config_step - returns session history on success
- /session/<session_id>/call_gen_env/<agent> - returns session history on success
- /session/<session_id>/history - returns session history on success
- /session/<session_id>/update_generated/<agent> - returns session history on success



## wei_gen flow
![weigen flow](https://res.cloudinary.com/dgmuzb9mm/image/upload/v1722982352/taoafbb2wsn9hjft9q4p.png)

### Steps
0. <u>Preparation</u>: Provide some sort of natural language description of the experiment along with values
0. <u>Validate experiment</u>: Provide all `/about`s from all instruments in the lab as context (≈7k tokens). Ask underlying model to check if the experiement described in the input from step 0 can be carried out with the available resources. Use token logprobs for this, over 50% "yes" prob as the the experiment will continue.
0. <u>Create experiment framework</u>: Using `/about`s as context, generate a structure for the experiment (using the input from step 0).
0. <u>Validate experiment framework</u>: Using the [z3 SMT Solver](https://github.com/Z3Prover/z3), check if the logical flow of the plan makes sense, retry generation with feedback if unsatisfiable.
0. <u>Make a short list of instruments to use</u>: Using `/about`s as context, make a short list of instruments to use as a precursor to the following step.
0. <u>Generate workflow</u>: Module `/about`s are fed as context, list of instruments from previous step provided as suggestion, retrieve 2-3 examples of workflows from vector db (RAG) and insert into context. Use the experiment framework from step 2 as guidance.
0. <u>Generate code</u>: Using previous messages as context, create python code logic for the entire experiment. Using an [AgentCoder](https://arxiv.org/abs/2312.13010v2) inspired scheme. 
0. <u>Generate misc</u>: Using the previous information as context, generate any extra documents (init locations of pipets, etc.). 


## History
A feature of wei_gen is the ability to load and store sessions. This enables wei_gen to not only be used in an iterative manner after an experiment is run (you can use wei_gen to help modify your workflow or code given errors that arose), but also allows wei_gen to work async. This enables wei_gen to be hosted as an API, as session data is persisted across various requests as long as a proper session UID is passed by the user.<br/>
An example a of a session history is below

```json

{
    "version": "0.0.1",
    "session_id": "f8954ec2-b1b4-413e-b566-ed4fe641536d",
    "timestamp": 0,
    "validity": 0.6,
    "original_user_description": "",
    "original_user_values": "",
    "framework_agent_ctx": None,
    "workflow_agent_ctx": None,
    "code_agent_ctx": None,
    "validator_agent_ctx": None,
    "config_agent_ctx": None,
    "generated_framework": "",
    "generated_code": "",
    "generated_workflow": "",
    "generated_config": "",
}
```

The idea is that this entire json document can also be sent to a front end and be parsed into a clean and friendly UI.



## Running wei_gen
To run any tests, check out the scripts in [/scripts](src/scripts/) that have various examples of testing the different functions accessible on the wei_gen session.

The weigen session class has the following functions that can be called on it
- def execute_experiment(self, user_description: str, user_values = None) -> None:
- def framework_step(self, user_description, user_values) -> None:
- def workflow_step(self) -> None:
- def code_step(self) -> None:
- def config_step(self) -> None:
- def call_gen_env(self, agent: str, user_input: str) -> str
- def modify_generated_data(self, agent: str, user_input: str) -> None
- def get_history(self) -> Dict[str, Any]



### Example usage
```python
from wei_gen import WEIGen
config_path = "<path to config>"
weigen = WEIGen(config_path)
weigen_session = weigen.new_session()
```

### Example config
```yaml
api_keys:
  openai: 
    key: "sk-..."
    org: "org-..."
settings:
  framework_model: "gpt-4-turbo"
  code_model: "gpt-4-turbo"
  validator_model: "gpt-4-turbo"
  workflow_model: "gpt-4-turbo"
```
*in future it might be easier to just have a config class that can be constructed within the code.

## V1/V2 Notes
V1
- Prompt templates
- All tool abouts are local, I think some are enhanced
- Critic ≈ validator
- Some plugging into pryankas work

V2
- Different flow of wei_gen
- Changed structure of agents
- Code/workflow gen upgraded
- Added history


## Notes
- Fine tuning a code llama for workflow gen could yield better results than gpt4.
