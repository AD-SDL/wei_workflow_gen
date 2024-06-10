import sys
sys.path.append('../wei_gen')

from wei_gen import WEIGen
config_path = "../../config.yaml"
weigen = WEIGen(config_path)
weigen_session = weigen.new_session()
test_input = """
Run PCR with 3 thermocycling cycles and seal plate for 20 minutes at 175 celsius. 
For the PCR liquid preparation and transfer, you have access to the following materials: 

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


values = """
1.) Transfer Biowater liquid 3 times with 676 uL each. Drop the tip on the last time. 
2.) Transfer 720 uL of 5x Reaction Buffer with 3 mix cycles and 500 uL mix volume per cycle. Drop the tip after. 
3.) Transfer 12 uL of DNA Polymerase 2 times with 3 mix cycles and 20 uL of mix volume per cycle. Drop the tip on the last time.
4.) Transfer 108 uL of DNTPs with 3 mix cycles and 600 uL of mix volume per cycle. Drop the tip after.
5.) Transfer 720 uL of GC Enhancer with 7 mix cycles and 700 uL of mix volume per cycle. Drop the tip after. 
6.) Transfer 15 uL of Master Mix liquid 2 times. Do not drop the tip. 
7.) Transfer 20 uL of forward primer liquid 1 times with 3 mix cycles and 15 uL of mix volume per cycle. Drop the tip. 
8.) Transfer 20 uL of backward primer liquid 1 times with 3 mix cycles and 15 uL of mix volume per cycle. Drop the tip. 
9.) Transfer 20 uL of template liquid 1 times with 3 mix cycles and 15 uL of mix volume per cycle. Drop the tip."""
weigen_session.execute_experiment(test_input, values)

