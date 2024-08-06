# wei_gen (v2)
wei_gen is a python package that takes a natural language description of an experiment and generates WEI workflows, code, and instrument configs. wei_gen is packaged as a class, and can be imported into any python project or spun up as an API. Examples of usage are in `/scripts`. An API-ized verion of wei_gen can be found in `/api`.

## Frontend
Interact with weigen with a [simple next.js app](https://github.com/nautsimon/wei-gen-client)

## wei_gen flow
0. <u>Preparation</u>: Provide some sort of natural language description of the experiment. Could be the product of some sort of white paper description, output from pryankas module, or just casually human generated dialogue.
0. <u>Validate experiment</u>: Using module `/about`s as context (≈5k tokens), check to see if the lab even has the tools to carry out the experiment (using the input from step 0). Use token logprobs for this, over 50% "yes" prob as the the experiment will continue.
0. <u>Create experiment framework</u>: Using module `/about`s as context, generate a structure for the experiment (using the input from step 0).
0. <u>Generate workflow</u>: Module `/about`s are fed as context, retrieve 2-3 examples of workflows from vector db (RAG) and insert into context. Use the experiment framework from step 2 as guidance.
0. <u>Generate code</u>: Using previous messages as context, create python code logic for the entire experiment. Using an [AgentCoder](https://arxiv.org/abs/2312.13010v2) inspired scheme. 
0. <u>Generate misc</u>: Using the previous information as context, generate any extra documents (init locations of pipets, etc.). 

## Workflow Gen
Currently refining this process but the general idea is that
1. <u>Determine if multiple workflows are needed</u>: Using experiment framework, the module abouts, and a hardcoded example of a multiple workflow system (from color picker), ask for yes/no response if multiple workflows will needed. With the logprobs returned, this will determine if the `gen_workflow` or the `gen_workflows` prompt will be used.
2. <u>Determine which instruments are needed</u>: Using the experiment framework and the module abouts, create a list of suggested instruments to use.
3. <u>Generate workflow</u>: With the list of the suggested instruments, the experiment framework, and 2 - 3 workflow examples using RAG, create a workflow.  


## History
A feature of wei_gen is the ability to load and store sessions. This enables wei_gen to not only be used in an iterative manner after an experiment is run (you can use wei_gen to help modify your workflow or code given errors that arose), but also allows wei_gen to work async. This enables wei_gen to be hosted as an API, as session data is persisted across various requests as long as a proper session UID is passed by the user.<br/>
An example a of a session history is below

```json
{
    "version": "0.0.1",
    "session_id": "f8954ec2-b1b4-413e-b566-ed4fe641536d",
    "timestamp": 0,
    "framework_agent_ctx": [],
    "workflow_agent_ctx": [],
    "code_agent_ctx": [],
    "validator_agent_ctx": [],
    "original_user_input": "",
    "generated_framework": "",
    "generated_code": "",
    "generated_workflow": [],
    "generated_config": [],
    "status": {
        "validation": false,
        "framework": false,
        "workflow": false,
        "code": false,
        "config": false,
    },
}
```

The idea is that this entire json document can also be sent to a front end and be parsed into a clean and friendly UI.

*ctx arrays's exclude agent system prompts.



## Running wei_gen
To run any tests, check out the scripts in [/scripts](src/scripts/) that have various examples of testing the different functions accessible on the wei_gen session.

The weigen session class has the following functions that can be called on it
- `gen_experiment_framework(self, user_input: str) -> str`
- `gen_code(self, content: str) -> None`
- `gen_workflow(self, user_input = "") -> None`
- `gen_extra_configs(self) -> None`
- `get_history -> json`



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










## Grouping of abouts
### Liquid Handling
- **Barty Liquid Manager** -> Actions: `drain_ink_all_motors`, `fill_ink_all_motors`, `refill_ink`
- **Opentrons OT2** -> Actions: `run_protocol`

### Plate Handling
- **Sealer Robot** -> Actions: `seal`
- **Brooks Xpeel** -> Actions: `peel`
- **Hudson Platecrane** -> Actions: `transfer`, `remove_lid`, `replace_lid`

### Data Acquisition
- **Epoch2 (BioTek Epoch2 Plate Reader)** -> Actions: `open`, `close`, `run_assay`
- **Hidex (Hidex Sense Microplate Reader)** -> Actions: `open`, `close`, `run_assay`
- **Camera Module** ->Actions: `take_picture`

### Robotic Manipulation
- **URRobotModule (UR3, UR5, UR16)** -> Actions: `transfer`, `remove_lid`, `replace_lid`
- **Pf400 Robotic Arm (Precise Automation PF400)** -> Actions: `transfer`, `remove_lid`, `replace_lid`

### Utilities
- **Sleep Module** -> Actions: `sleep`

### Gate and Process Control
- **FOM** -> Actions: `open_gate`, `close_gate`, `run_fom`
- **KLA** -> Actions: `open_gate`, `close_gate`, `run_kla`

### Tools
- **HiG4 Centrifuge (BioNex HiG 4 Automated Centrifuge)** -> Actions: `spin`, `open_shield`, `close_shield`, `home`, `abort_spin`
- **Biometra (Analytik Jena Biometra TRobot II)** -> Actions: `run_protocol`, `open_lid`, `close_lid`, `get_status`


See the current array of modules and their tags in [/src/wei_gen/instruments.json](/src/wei_gen/instruments.json)


## Missing Abouts (not included in wei_gen)
- https://github.com/AD-SDL/brooks_xpeel_module_ros
- https://github.com/AD-SDL/henry_module
- https://github.com/AD-SDL/pf400_module_ros
- https://github.com/AD-SDL/a4s_sealer_module_ros
- https://github.com/AD-SDL/ot2_module_ros/blob
- https://github.com/AD-SDL/hudson_platecrane_module_ros
- https://github.com/AD-SDL/hidex_module_ros
- https://github.com/AD-SDL/biometra_module_ros
- https://github.com/AD-SDL/hudson_solo_module
- https://github.com/AD-SDL/camera_module_ros
- https://github.com/AD-SDL/tecan_module
- https://github.com/AD-SDL/ur_module_ros
- https://github.com/AD-SDL/liconic_module
- https://github.com/AD-SDL/mir_module
- https://github.com/AD-SDL/aps_workcell
- https://github.com/AD-SDL/barty_module
- https://github.com/AD-SDL/biostack_module
- https://github.com/AD-SDL/kla_module




## Notes
 - the ui will parse code or yaml and use that to update generated data. 
 - 
