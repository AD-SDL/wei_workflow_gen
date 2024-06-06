import sys
sys.path.append('../wei_gen')

from wei_gen import WEIGen
config_path = "../../config.yaml"
weigen = WEIGen(config_path)
weigen_session = weigen.new_session("2381ceff-fc98-45a4-aa1d-f51fb5a3e2df")

weigen_session.call_gen_env("framework", "Can you delete the last step")

