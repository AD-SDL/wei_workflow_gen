import sys
sys.path.append('../wei_gen')

from wei_gen import WEIGen
config_path = "../../config.yaml"
weigen = WEIGen(config_path)
weigen_session = weigen.load_session("d060ebac-82bb-4ccb-a7aa-c089bfe7943e")
weigen_session.gen_orchestration("""
Can you add a final step to transmit data to the cloud?
""")




