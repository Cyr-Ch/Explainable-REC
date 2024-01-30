import csv


def read_questions_db(path_to_q_db):
    q_list = list()
    with open(path_to_q_db, "r") as q_db:
        csv_reader = csv.reader(q_db)
        for line in csv_reader:
            #print(line)
            q_list.append(line)
    
    return q_list


def icl_code_generator(path_to_q_db):
    q_db = read_questions_db(path_to_q_db)
    
    icl_code =""
    for question in range(1,len(q_db)):
        if len(q_db[question]) > 1:
            icl_code += q_db[question][0]+'\n'+q_db[question][1]+'\n'
    return icl_code
         

def icl_interpreter(path_to_q_db):
    q_db = read_questions_db(path_to_q_db)
    icl_interpreter =""
    for question in range(1,len(q_db)):
        icl_interpreter += q_db[question][2]+'\n'+q_db[question][3]+'\n'
    return icl_interpreter
