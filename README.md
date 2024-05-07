# wei_gen

### Liquid Handling
- **Barty Liquid Manager**
  - Actions: `drain_ink_all_motors`, `fill_ink_all_motors`, `refill_ink`
- **Opentrons OT2**
  - Actions: `run_protocol`

### Plate Handling
- **Sealer Robot**
  - Actions: `seal`
- **Brooks Xpeel**
  - Actions: `peel`
- **Hudson Platecrane**
  - Actions: `transfer`, `remove_lid`, `replace_lid`

### Data Acquisition
- **Epoch2 (BioTek Epoch2 Plate Reader)**
  - Actions: `open`, `close`, `run_assay`
- **Hidex (Hidex Sense Microplate Reader)**
  - Actions: `open`, `close`, `run_assay`

### Camera Module
- Actions: `take_picture`

### Robotic Manipulation
- **URRobotModule (UR3, UR5, UR16)**
  - Actions: `transfer`, `remove_lid`, `replace_lid`
- **Pf400 Robotic Arm (Precise Automation PF400)**
  - Actions: `transfer`, `remove_lid`, `replace_lid`

### Utilities
- **Sleep Module**
  - Actions: `sleep`

### Gate and Process Control
- **FOM**
  - Actions: `open_gate`, `close_gate`, `run_fom`
- **KLA**
  - Actions: `open_gate`, `close_gate`, `run_kla`

### Tools
- **HiG4 Centrifuge (BioNex HiG 4 Automated Centrifuge)**
  - Actions: `spin`, `open_shield`, `close_shield`, `home`, `abort_spin`
- **Biometra (Analytik Jena Biometra TRobot II)**
  - Actions: `run_protocol`, `open_lid`, `close_lid`, `get_status`

## Missing Abouts
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

## things to improve upon on the module `/about` endpoints
- need to define any set ranges or valid values
- dependencies
- workflow examples



## Flow
0. Preparation: Provide some sort of natural language description of the experiment. Could be the product of some sort of experiment generation, the orchestrator, or a human.
1. Generate workflow: Module `/about`s are fed as context (≈5k tokens), retrieve 2/3 examples of workflows from vector db and insert into context.
2. Generate code logic: Using previous messages as context, create python code logic for the entire experiment. Use coder agent scheme. In the future, this step should also use RAG to get similar code snippet examples. (should be in cli format).
3. Any extras: eg. location configs