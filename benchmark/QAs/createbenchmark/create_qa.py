import csv
import random 
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import subprocess
import re
from typing import Dict, List, Optional, Union

from eventlet.timeout import Timeout

VALUE_PROSUMER=[1,2,3,4]
VALUE_TIMESTEP=[1,2,3]
DATA_CODE_STR = "# OPTIGUIDE DATA CODE GOES HERE"
CONSTRAINT_CODE_STR = "# OPTIGUIDE CONSTRAINT CODE GOES HERE"

def VALUE_PERCENTAGE():
    return random.choice([i for i in range(101)])

def create_combinations(prosumer, timestep, percentage, num_combinations=5):
    # Generate different combinations
    combinations = []
    if percentage:
        for _ in range(num_combinations):
            combination = {}

            if prosumer:
                combination['{{VALUE_PROSUMER}}'] = random.choice(VALUE_PROSUMER)-1

            if timestep:
                combination['{{VALUE_TIMESTEP}}'] = random.choice(VALUE_TIMESTEP)-1

            
            combination['{{VALUE_PERCENTAGE}}'] = VALUE_PERCENTAGE()
            combinations.append(combination)
    
    elif prosumer and timestep:
        for pro in VALUE_PROSUMER:
            for t in VALUE_TIMESTEP:
                combination = {}
                combination['{{VALUE_PROSUMER}}'] = pro-1
                combination['{{VALUE_TIMESTEP}}'] = t-1
                combinations.append(combination)

    elif prosumer:
        for pro in VALUE_PROSUMER:
            combination = {}
            combination['{{VALUE_PROSUMER}}'] = pro-1
            combinations.append(combination)

    elif timestep:
        for t in VALUE_TIMESTEP:
            combination = {}
            combination['{{VALUE_TIMESTEP}}'] = t-1
            combinations.append(combination)


    return combinations

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

def compute_gt_questions(file_path, opt_script):
    # Read the original Python script
    with open(opt_script, 'r') as script_file:
        original_script = script_file.read()

    data_dict = {}
    
    with open(file_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        counter = 0
        for row in csv_reader:
            #print(row)
            question = row['\ufeffQuestion']
            gt_code = row['GT Code']
            gt_obj_value = row['GT Objective Value']
            sgp_code = row['SGP Code']
            sgp_obj_value = row['SGP Objective Value']
            
            prosumer = "{{VALUE_PROSUMER}}" in question
            timestep = "{{VALUE_TIMESTEP}}" in question
            percentage = "{{VALUE_PERCENTAGE}}" in question
            combinations_question = create_combinations(prosumer, timestep, percentage, num_combinations=5)

            #print(combinations_question)
            for comb_question in combinations_question:
                counter +=1
                final_question = question
                final_gt_code = gt_code
                for value in comb_question.keys():
                    if value == "{{VALUE_PERCENTAGE}}":
                       final_question = final_question.replace(value, str(int(comb_question[value]))) 
                    else: 
                        final_question = final_question.replace(value, str(int(comb_question[value])+1))
                    final_gt_code = final_gt_code.replace(value, str(comb_question[value]))
                    #print("Printing value")
                    #print(value)
                    #print("Printing the content of value")
                    #print(comb_question[value])
                    #print("printing the question")
                    #print(final_question)
                    #print("printing the code")
                    #print(final_gt_code)

                data_dict[final_question] = {
                'GT Code': final_gt_code,
                'GT Objective Value': gt_obj_value,
                'SGP Code': sgp_code,
                'SGP Objective Value': sgp_obj_value
                }
                
                # Add the line to the script
                modified_script =  _insert_code(original_script, final_gt_code)
                # Write the modified script to a temporary file
                temp_script_path = '/Users/cchaabani/Documents/GitRepo/SGP-Chat/benchmark/QAs/createbenchmark/temp_scripts_pimp_pexp_easy/temp_script'+str(counter)+'.py'
                with open(temp_script_path, 'w') as temp_script_file:
                    temp_script_file.write(modified_script)

                # Execute the modified script
                execution_rst = _run_with_exec(modified_script)
                print(execution_rst)
                data_dict[final_question]['GT Objective Value'] = execution_rst
                
    
    with open(file_path.replace(".csv", "_processed.csv"), 'w', newline='') as csvfile:
        fieldnames = ['Question', 'GT Code', 'GT Objective Value', 'SGP Code', 'SGP Objective Value']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Writing the header
        csv_writer.writeheader()

        # Writing dictionary entries
        for question, values in data_dict.items():
            csv_writer.writerow({'Question': question, **values})

    


