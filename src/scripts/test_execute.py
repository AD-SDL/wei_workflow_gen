import sys
sys.path.append('../wei_gen')

from wei_gen import WEIGen
config_path = "../../config.yaml"
weigen = WEIGen(config_path)
weigen_session = weigen.new_session()
test_input = """
Im trying to make a PCR testing experiment, here are some details 
Run PCR with 3 thermocycling cycles and seal plate for 20 minutes at 175 celsius. For the PCR liquid preparation and transfer, you have access to the following materials: 

Master Mix:
1.) Biowater (10 mL) 
2.) 5x Reaction Buffer (~1mL) 
3.) DNA Polymerase (~40ul) 
4.) DNTPs (~200 uL) 
5.) GC Enhancer (~1mL)
6.) Empty tube to store materials 1.) to 5.) 

DNA:
7.) Forward Primers (~20ul per well)
8.) Reverse primers(~20ul per well)
9.) Template DNA strands (~20ul per well)
10.) Final Plate for all materials
"""
weigen_session.execute_experiment(test_input)

