import oyaml as yaml

def preprocess_raw_output(output_string:str) -> str:
    """Pre-processes raw_output by parsing through 'Output:' string"""
    output_start = output_string.find("Output:")
    if output_start == -1:
        return None
    output_lines = output_string[output_start + len("Output:"):].strip().split('\n')
    parsed_output = "\n".join(output_lines).strip()
    return parsed_output

def parse_ot2_block(parsed_block:dict) -> dict:
    """Takes in parsed_block as [dict] and then parses it into a dict:{name of block, dict, error} or error:str
    
    Parameters:
    ==========
    parsed_block: dict
      single yaml block in a list of yaml blocks 

    Outputs (Dict):
    ===============
    name: str
      name of the yaml block ex. biometra 
    code: dict 
      dict that represents yaml block code
    error: str
      error from running yaml block through parser
    """
    # TODO: fix this issue: if -name is missing, then set() will make it so that it still passes the assert test
    # demo: use the string block, but remove a "- name:" block 
    valid_keys = ['name', 'source', 'destination', 'volume', 'mix_cycles', 'mix_volume', 'drop_tip']
    main_args = [block_key for block_key in parsed_block.keys()]
    try: 
        assert set(main_args) == set(valid_keys), f"""The '{parsed_block["name"]}' yaml block is missing some necessary arguments. All arguments {valid_keys} must be present for your output to be valid"""
        code = {
            "name":parsed_block["name"],
            "source":parsed_block["source"],
            "destination":parsed_block["destination"],
            "volume":parsed_block["volume"], 
            "mix_cycles":parsed_block["mix_cycles"], 
            "mix_volume":parsed_block["mix_volume"], 
            "drop_tip":parsed_block["drop_tip"]
        }
        return code
    except Exception as e: 
        error = e
        return f"Error parsing yaml output (before program execution):\n{error}"
    
def parse_ot2(raw_yaml:str) -> dict:
    """Takes in the raw_yaml of yaml blocks from GPT. It iterates through parsed data 
    and sends each block into parse_ot2_block(), and returns a dict{code, error} if success 
    and str if fail. It then appends the dict or str into a yaml block list and error list. 
    If yaml block fails, exit early with str error; else returns {list[dict], list}

    Parameters:
    ==========
    raw_yaml: str
      A large string that contains all of the directions for the ot2 reaction in yaml block format

    Output (Dict):
    =======
    ot2_yaml: list
      A list that contains the yaml blocks for each step in the ot2 reaction 
    error_list: list
      A list that contains the errors from outputing the 
    """
    ot2_yaml = []
    assert yaml.safe_load(raw_yaml), f"""Your yaml output is not in the yaml proper format to be parsed into a yaml dictionary via yaml.safe_load(). Please refer to the format guidelines given to you."""
    parsed_data = yaml.safe_load(raw_yaml)
    for _, block in enumerate(parsed_data): 
        result = parse_ot2_block(block)
        if type(result) == str: 
            # if error, return error str
            return result
        # else, append to ot2 code
        ot2_yaml.append(result)
    return ot2_yaml

# DONE
def parse_sciclops(raw_yaml:str) -> dict:
    """Takes in raw_yaml as yaml str and then parses it into a dict:{str, dict, error} or error:str"""
    valid_keys = ['name', 'module', 'action', 'args']
    valid_arg_keys = ['loc']
    try:
        assert yaml.safe_load(raw_yaml), f"""{raw_yaml}\nIs not in the yaml proper format for sciclops to be parsed into a yaml dictionary via yaml.safe_load()"""
        parsed_output = yaml.safe_load(raw_yaml)
        main_args = [key for element in parsed_output for key in element.keys()]
        assert set(main_args) == set(valid_keys), f"""{raw_yaml}\nIs missing necessary arguments for sciclops tool. It must have all arguments: {valid_keys}"""
        assert parsed_output[3]["args"] != None, f"{raw_yaml}\nIs missing necessary inputs for args for sciclops tool. It must have all arguments: {valid_arg_keys}"

        code = {"name":parsed_output[0]["name"], 
                    "module":parsed_output[1]["module"],
                    "action":parsed_output[2]["action"], 
                    "args": {
                        "loc": parsed_output[3]["args"][0]["loc"]
                    }
        }
        return code
    except Exception as e: 
        error = e
        return f"Error parsing yaml output (before program execution):\n{error}"

# Done
def parse_pf400(raw_yaml:str) -> str:  
    """Takes in raw_yaml as yaml str and then parses it into a dict:{str, dict, error} or error:str"""
    valid_keys = ['name', 'module', 'action', 'args']
    valid_arg_keys = ['source', 'target', 'source_plate_rotation', 'target_plate_rotation']   
    try: 
        assert yaml.safe_load(raw_yaml), f"""{raw_yaml}\nIs not in the yaml proper format for pf400 to be parsed into a yaml dictionary via yaml.safe_load()"""
        parsed_output = yaml.safe_load(raw_yaml)
        main_args = [key for element in parsed_output for key in element.keys()]
        assert set(main_args) == set(valid_keys), f"""{raw_yaml}\nIs missing necessary arguments for pf400 tool. It must have all arguments: {valid_keys}"""
        sub_args = [key for element in parsed_output[3]["args"] for key in element.keys()]
        assert set(sub_args) == set(valid_arg_keys), f"""{raw_yaml}\nIs missing necessary inputs for args for pf400 tool. It must have all arguments: {valid_arg_keys}"""

        source = parsed_output[3]["args"][2]["source_plate_rotation"]
        target = parsed_output[3]["args"][3]["target_plate_rotation"]
        code = {"name":parsed_output[0]["name"], 
                    "module":parsed_output[1]["module"],
                    "action":parsed_output[2]["action"], 
                    "args": {
                        "source": parsed_output[3]["args"][0]["source"],
                        "target": parsed_output[3]["args"][1]["target"], 
                        "source_plate_rotation": source,
                        "target_plate_rotation": target
                    }
        }
        return code
    except Exception as e:
        error = e 
        return f"Error parsing yaml output (before program execution):\n{error}"

# Done
def parse_biometra(raw_yaml:str) -> str:
    """Takes in raw_yaml as yaml str and then parses it into a dict:{dict, error} or error:str""" 
    valid_keys_default = ['name', 'module', 'action']
    valid_keys_program = ['name', 'module', 'action', 'args']
    valid_arg_keys = ['program_n']
    try: 
        assert yaml.safe_load(raw_yaml), f"""{raw_yaml}\nIs not in the yaml proper format for biometra to be parsed into a yaml dictionary via yaml.safe_load()"""
        parsed_output = yaml.safe_load(raw_yaml)
        if len(parsed_output) > 3 and 'args' in parsed_output[3]:
            main_args = [key for element in parsed_output for key in element.keys()]
            assert set(main_args) == set(valid_keys_program), f"""{raw_yaml}\nIs missing necessary arguments for biometra tool. It must have all arguments: {valid_keys_program}"""
            assert len(parsed_output[3]["args"]) != 0, f"{raw_yaml}\nIs missing necessary inputs for args for biometra tool. It must have all arguments: {valid_arg_keys}"
        else: 
            main_args = [key for element in parsed_output for key in element.keys()]
            assert set(main_args) == set(valid_keys_default), f"""{raw_yaml}\nIs missing necessary arguments for biometra tool. It must have all arguments: {valid_keys_default}"""

        code = {'name': parsed_output[0]['name'],
                'module': parsed_output[1]['module'],
                'action': parsed_output[2]['action'],
            }
        if len(parsed_output) > 3 and 'args' in parsed_output[3]:
            code['args'] = {'program_n':parsed_output[3]["args"][0]["program_n"]}
        return code
    except Exception as e:
        error = e 
        return f"Error parsing yaml output (before program execution):\n{error}"
    
# Done
def parse_peeler(raw_yaml:str) -> str:
    """Takes in raw_yaml as yaml str and then parses it into a dict:{dict, error} or error:str"""
    valid_keys = ['name', 'module', 'action']
    try: 
        assert yaml.safe_load(raw_yaml), f"""{raw_yaml}\nIs not in the yaml proper format for peeler to be parsed into a yaml dictionary via yaml.safe_load()"""
        parsed_output = yaml.safe_load(raw_yaml)
        main_args = [key for element in parsed_output for key in element.keys()]
        assert set(main_args) == set(valid_keys), f"""{raw_yaml}\nIs missing necessary arguments for peeler tool. It must have all arguments: {valid_keys}"""
        code = {"name":parsed_output[0]["name"], 
                    "module":parsed_output[1]["module"],
                    "action":parsed_output[2]["action"]
                    }
        return code
    except Exception as e:
        error = e 
        return f"Error parsing yaml output (before program execution):\n{error}"

# Done
def parse_sealer(raw_yaml:str) -> str: 
    """Takes in raw_yaml as yaml str and then parses it into a dict:{dict, error} or error:str"""
    valid_keys = ['name', 'module', 'action', 'args']
    valid_arg_keys = ['time', 'temperature']   
    try: 
        assert yaml.safe_load(raw_yaml), f"""{raw_yaml}\nIs not in the yaml proper format for sealer to be parsed into a yaml dictionary via yaml.safe_load()"""
        parsed_output = yaml.safe_load(raw_yaml)
        main_args = [key for element in parsed_output for key in element.keys()]
        assert set(main_args) == set(valid_keys), f"""{raw_yaml}\nIs missing necessary arguments for sealer tool. It must have all arguments: {valid_keys}"""
        sub_args = [key for element in parsed_output[3]["args"] for key in element.keys()]
        assert set(valid_arg_keys) == set(sub_args), f"""{raw_yaml}\nIs missing necessary inputs for args for sealer tool. It must have all arguments: {valid_arg_keys}"""

        code = {"name":parsed_output[0]["name"], 
                    "module":parsed_output[1]["module"],
                    "action":parsed_output[2]["action"], 
                    "args": {
                        "time": parsed_output[3]["args"][0]["time"],
                        "temperature": parsed_output[3]["args"][1]["temperature"], 
                    }
        }
        return code
    except Exception as e:
        error = e 
        return f"Error parsing yaml output (before program execution):\n{error}"
    

if __name__ == "__main__": 
    
  # raw_output = load_test_output(test="ot2")

  # processed_sciclops = load_test_output(test="sciclops", status="incorrect")
  # wrong_result = parse_sciclops(processed_sciclops)

  # proc_sciclops = load_test_output(test="sciclops", status="correct")
  # right_result = parse_sciclops(proc_sciclops)

  # processed_wrong = load_test_output(test="pf400", status="incorrect")
  # wrong_result = parse_pf400(processed_wrong)

  # processed_right = load_test_output(test="pf400", status="correct")
  # right_result = parse_pf400(processed_right)

  # processed_right = load_test_output(test="biometra_run", status="correct")
  # right_result = parse_biometra(processed_right)

  # processed_wrong = load_test_output(test="biometra_run", status="incorrect")
  # wrong_result = parse_biometra(processed_wrong)

  # processed_right = load_test_output(test="peeler", status="correct")
  # right_result = parse_peeler(processed_right)

  # processed_wrong = load_test_output(test="peeler", status="incorrect")
  # wrong_result = parse_peeler(processed_wrong)

  # processed_right = load_test_output(test="sealer", status="correct")
  # right_result = parse_sealer(processed_right)

  # processed_wrong = load_test_output(test="sealer", status="incorrect")
  # wrong_result = parse_sealer(processed_wrong)


  # processed_right = load_test_output(test="ot2", status="correct")
  # right_result = parse_ot2(processed_right)

#   processed_wrong = load_test_output(test="ot2", status="incorrect")
#   wrong_result = parse_ot2(processed_wrong)

  print("End Test")



  



