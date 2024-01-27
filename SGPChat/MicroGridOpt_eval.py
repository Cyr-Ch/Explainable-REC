import csv
import openai
import gurobipy as gp
from gurobipy import GRB
from typing import Dict, List, Optional, Union
import re
import numpy as np
from eventlet.timeout import Timeout
import time
import os 

DATA_CODE_STR = "# OPTIGUIDE DATA CODE GOES HERE"
CONSTRAINT_CODE_STR = "# OPTIGUIDE CONSTRAINT CODE GOES HERE"


WRITER_SYSTEM_MSG = """You are a chatbot to:
(1) write Python code to answer users questions for microgrid energy management coding
project;
(2) explain solutions from a Gurobi/rsome/Python solver.

--- SOURCE CODE ---
{source_code}

--- DOC STR ---
{doc_str}
---

Here are some example questions and their answers and codes:
--- EXAMPLES ---
{example_qa}
---

The execution result of the original source code is below.
--- Original Result ---
{execution_result}

Note that your written code will be added to the lines with substring:
"# OPTIGUIDE *** CODE GOES HERE"
So, you don't need to write other code, such as m.optimize() or m.update() or m.solve() or model.update() or model.reset() or model.solve().
You just need to write the python code to be added.
So please only write back the lines of python code to be added and nothing else. No explanation and no additional text only the executable code.
When the user uses the term timestep 1, they refer to t=0 in our optimization problem.
"""

def _replace(src_code: str, old_code: str, new_code: str) -> str:
    """
    Inserts new code into the source code by replacing a specified old
    code block.

    Args:
        src_code (str): The source code to modify.
        old_code (str): The code block to be replaced.
        new_code (str): The new code block to insert.

    Returns:
        str: The modified source code with the new code inserted.

    Raises:
        None

    Example:
        src_code = 'def hello_world():\n    print("Hello, world!")\n\n# Some
        other code here'
        old_code = 'print("Hello, world!")'
        new_code = 'print("Bonjour, monde!")\nprint("Hola, mundo!")'
        modified_code = _replace(src_code, old_code, new_code)
        print(modified_code)
        # Output:
        # def hello_world():
        #     print("Bonjour, monde!")
        #     print("Hola, mundo!")
        # Some other code here
    """
    pattern = r"( *){old_code}".format(old_code=old_code)
    head_spaces = re.search(pattern, src_code, flags=re.DOTALL).group(1)
    new_code = "\n".join([head_spaces + line for line in new_code.split("\n")])
    rst = re.sub(pattern, new_code, src_code)
    return rst


def _insert_code(src_code: str, new_lines: str) -> str:
    """insert a code patch into the source code.


    Args:
        src_code (str): the full source code
        new_lines (str): The new code.

    Returns:
        str: the full source code after insertion (replacement).
    """
    if new_lines.find("addConstr") >= 0:
        return _replace(src_code, CONSTRAINT_CODE_STR, new_lines)
    else:
        return _replace(src_code, DATA_CODE_STR, new_lines)
    
def _run_with_exec(src_code: str) -> Union[str, Exception]:
    """Run the code snippet with exec.

    Args:
        src_code (str): The source code to run.

    Returns:
        object: The result of the code snippet.
            If the code succeed, returns the objective value (float or string).
            else, return the error (exception)
    """
    locals_dict = {}
    locals_dict.update(globals())
    locals_dict.update(locals())

    timeout = Timeout(
        60,
        TimeoutError("This is a timeout exception, in case "
                     "GPT's code falls into infinite loop."))
    try:
        exec(src_code, locals_dict, locals_dict)
    except Exception as e:
        return e
    finally:
        timeout.cancel()

    try:
        status = locals_dict["m"].Status
        if status != GRB.OPTIMAL:
            if status == GRB.UNBOUNDED:
                ans = "unbounded"
            elif status == GRB.INF_OR_UNBD:
                ans = "inf_or_unbound"
                m = locals_dict["m"]
                m.computeIIS()
                constrs = [c.ConstrName for c in m.getConstrs() if c.IISConstr]
                ans += "\nConflicting Constraints:\n" + str(constrs)
            elif status == GRB.INFEASIBLE:
                ans = "infeasible"
                m = locals_dict["m"]
                m.computeIIS()
                constrs = [c.ConstrName for c in m.getConstrs() if c.IISConstr]
                ans += "\nConflicting Constraints:\n" + str(constrs)
            else:
                ans = "Model Status:" + str(status)
        else:
            ans = str(locals_dict["m"].objVal)
    except Exception as e:
        return e

    return ans

def compute_gt_questions(file_path, opt_script, example_qa_code, openaikey, model="gpt-4"):
    # Read the original Python script
    with open(opt_script, 'r') as script_file:
        original_script = script_file.read()
    
    data_dict = {}
    if os.path.exists(file_path.replace(".csv", "_finalprocessed.csv")):
        with open(file_path.replace(".csv", "_finalprocessed.csv"), 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                question = row['Question']
                data_dict[question] = {
                    'GT Code': row['GT Code'],
                    'GT Objective Value': row['GT Objective Value'],
                    'SGP Code': row['SGP Code'],
                    'SGP Objective Value': row['SGP Objective Value']
                    }
            

    
    
    with open(file_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        counter = 0
        for row in csv_reader:
            counter += 1
            question = row['Question']
            if question not in data_dict.keys():
                gt_code = row['GT Code']
                gt_obj_value = row['GT Objective Value']

                    
                writer_sys_msg = WRITER_SYSTEM_MSG.format(
                    source_code=original_script,
                    doc_str="",
                    example_qa=example_qa_code,
                    execution_result=gt_obj_value,
                )

                openai.api_key = openaikey

                # Send the question to GPT-3
                
                response = openai.ChatCompletion.create(
                model="gpt-4",  # Use the appropriate GPT-3 model
                messages=[
                        {"role": "system", "content": writer_sys_msg},
                        {"role": "user", "content": question},
                    ]
                )

                # Get and print the GPT-3 response
                gpt4_reply = response['choices'][0]['message']['content']
                print("GPT-4 Reply:", gpt4_reply)
                
                #res = 
                    
                # Add the line to the script
                modified_script =  _insert_code(original_script, gpt4_reply.replace("Answer Code:","").replace("python ", "").replace("python", "").replace("```",""))
                print(modified_script)
                # Write the modified script to a temporary file
                    

                # Execute the modified script
                execution_rst = _run_with_exec(modified_script)
                print(execution_rst)
                data_dict[question] = {
                    'GT Code': gt_code,
                    'GT Objective Value': gt_obj_value,
                    'SGP Code': gpt4_reply.replace("Answer Code:","").replace("python ", "").replace("```","").replace("\"", ""),
                    'SGP Objective Value': execution_rst
                    }
                with open(file_path.replace(".csv", "_finalprocessed.csv"), 'w', newline='') as csvfile:
                    fieldnames = ['Question', 'GT Code', 'GT Objective Value', 'SGP Code', 'SGP Objective Value']
                    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Writing the header
                    csv_writer.writeheader()

                    # Writing dictionary entries
                    for question, values in data_dict.items():
                        csv_writer.writerow({'Question': question, **values})

                time.sleep(3)
                        
    
    
    
