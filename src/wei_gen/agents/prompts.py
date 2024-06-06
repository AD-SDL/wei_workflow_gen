INITIAL_ORCHESTRATION_PROMPT = [
    {
        "role": "system",
        "content": "Assume the role of a intelligent and experienced scientist. You will be tasked with orchestrating a step by step experiment plan given a list of instruments and user input. ",
    }
]
# TODO, provide examples, maybe after testing and getting more data


def gen_coder_prompt(code_str):
    return f"""**Role**: You are a software programmer.
**Task**: As a programmer, you are required to complete the function. Use a Chain-of-Thought approach to break
down the problem, create pseudocode, and then write the code in Python language. Ensure that your code is
efficient, readable, and well-commented.
For example:
**Input Code Snippet**:
```python
{code_str}
# Add your code here to complete the function
```
**Instructions**:
1. **Understand and Clarify**: Make sure you understand the task.
2. **Algorithm/Method Selection**: Decide on the most efficient way.
3. **Pseudocode Creation**: Write down the steps you will follow in pseudocode.
4. **Code Generation**: Translate your pseudocode into executable Python code."""

PYDANTIC_WORKFLOW_CLASSES = '''
class Workflow(BaseModel):
    """Grand container that pulls all info of a workflow together"""

    name: str
    """Name of the workflow"""
    modules: List[SimpleModule]
    """List of modules needed for the workflow"""
    flowdef: List[Step]
    """User Submitted Steps of the flow"""
    metadata: Metadata = Field(default_factory=Metadata)
    """Information about the flow"""

class SimpleModule(BaseModel):
    """Simple module for use in the workflow file (does not need as much info)"""

    name: str
    """Name, should correspond with a module ros node"""

class Step(BaseModel, arbitrary_types_allowed=True):
    """Container for a single step"""

    name: str
    """Name of step"""
    module: str
    """Module used in the step"""
    action: str
    """The command type to get executed by the robot"""
    args: Dict[str, Any] = {}
    """Arguments for instruction"""
    checks: Optional[str] = None
    """For future use"""
    locations: Dict[str, Any] = {}
    """locations referenced in the step"""
    requirements: Dict[str, Any] = {}
    """Equipment/resources needed in module"""
    dependencies: List[str] = []
    """Other steps required to be done before this can start"""
    priority: Optional[int] = None
    """For scheduling"""
    id: str = Field(default_factory=ulid_factory)
    """ID of step"""
    comment: Optional[str] = None
    """Notes about step"""

    start_time: Optional[datetime] = None
    """Time the step started running"""
    end_time: Optional[datetime] = None
    """Time the step finished running"""
    duration: Optional[timedelta] = None
    """Duration of the step's run"""
    result: Optional["StepResponse"] = None
    """Result of the step after being run"""

    # Load any yaml arguments
    @validator("args")
    def validate_args_dict(cls, v: Any, **kwargs: Any) -> Any:
        """asserts that args dict is assembled correctly"""
        assert isinstance(v, dict), "Args is not a dictionary"
        for key, arg_data in v.items():
            try:
                arg_path = Path(arg_data)
                # Strings can be path objects, so check if exists before loading it
                if not arg_path.exists():
                    return v
                else:
                    print(arg_path)
                    print(arg_path.suffix)
                if arg_path.suffix == ".yaml" or arg_path.suffix == ".yml":
                    print(f"Loading yaml from {arg_path}")
                    v[key] = yaml.safe_load(arg_path.open("r"))
                    print(v[key])
            except TypeError:  # Is not a file
                pass

        return v

class Metadata(BaseModel):
    """Metadata container"""

    author: Optional[str] = None
    """Who authored this workflow"""
    info: Optional[str] = None
    """Long description"""
    version: float = 0.1
    """Version of interface used"""
'''


PYDANTIC_CONFIG_CLASSES = '''


'''

INITIAL_WORKFLOW_PROMPT = [
    {
        "role": "system",
        "content": f"Assume the role of an intelligent assistant tasked with generating a YAML workflow for an experiment. The generated YAML file must adhere to the structure and specifications defined by these Pydantic classes: {PYDANTIC_WORKFLOW_CLASSES}. Your output will be evaluated based on its compliance with these classes.",
    }
]

INITIAL_CODE_PROMPT = [
    {
        "role": "system",
        "content": """**Role**: You are a software programmer.
**Task**: As a programmer, you are required to write a python file given a specific prompt. Use a Chain-of-Thought approach to break
down the problem, create pseudocode, and then write the code in Python language. Ensure that your code is
efficient, readable, and well-commented.
For example, here is a file you might create:
```python
#!/usr/bin/env python3

from pathlib import Path
from wei import Experiment
from time import sleep


def main():
    # Connect to the experiment
    exp = Experiment("127.0.0.1", "8000", "<TEST NAME>")
    exp.register_exp()
    
    # run the workflow
    wf_path = Path(
        "<PATH TO WORKFLOW>"
    )

    flow_info = exp.run_job(wf_path.resolve())
    print(flow_info)

    # wait for the job to finish
    while True: 
        flow_state = exp.query_job(flow_info["job_id"])
        print(flow_state)
        if flow_state["status"] == "failed" or flow_state["status"] == "success":
            break
        sleep(1)


if __name__ == "__main__":
    main()
```

**Instructions**:
1. **Algorithm/Method Selection**: Decide on the most efficient way.
2. **Pseudocode Creation**: Write down the steps you will follow in pseudocode.
3. **Code Generation**: Translate your pseudocode into executable Python code.""",
    }
]

INITIAL_VALIDATOR_PROMPT = [
    {
        "role": "system",
        "content": "Assume the role of a intelligent assistant tasked with validating and debugging code. You will receive instructions to generate test cases and will use this to test code previously generated. Should any errors arise after running the tests, you will provide well thought out, insightful feedback.",
    }
]

INITIAL_INSTRUMENT_PROMPT = [
    {
        "role": "system",
        "content": "Assume the role of an intelligent assistant tasked with generating a YAML config and instrument/robot that is used in an experiment.",
    }
]