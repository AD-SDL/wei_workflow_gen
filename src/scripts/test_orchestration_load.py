import sys
sys.path.append('../wei_gen')

from wei_gen import WEIGen
config_path = "../../config.yaml"
weigen = WEIGen(config_path)
weigen_session = weigen.load_session("1e2b29a5-ec39-4cd7-a4ae-3900e7949b02")
weigen_session.gen_orchestration("""
Can you add a final step to transmit data to the cloud?
""")




