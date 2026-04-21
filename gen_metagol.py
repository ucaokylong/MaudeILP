import re
import os

def parse_metagol_line(line):
    line = line.strip()
    if not line or line.startswith(('%', ':-')): 
        return None
    if re.match(r'^(pos|neg)\((.*)\)\.$', line): 
        return line 
    m_fact = re.match(r'^(\w+)\((.*)\)\.$', line)
    if m_fact: 
        return line, m_fact.group(1), len(m_fact.group(2).split(','))
    return None

def convert_to_metagol():
    bk, pos, neg = [], [], []
    preds = set()

    for file in ['bk.pl', 'exs.pl']:
        if not os.path.exists(file): continue
        with open(file, 'r') as f:
            for line in f:
                res = parse_metagol_line(line)
                if not res: continue
                if isinstance(res, str):
                    if res.startswith('pos('): pos.append(res)
                    else: neg.append(res)
                else:
                    fact_str, pred_name, arity = res
                    bk.append(fact_str)
                    preds.add(f"{pred_name}/{arity}")

    with open('1d_flip_metagol.pl', 'w') as f:
        f.write(":- use_module('../metagol').\nmetagol:functional.\n\n")
        f.write("%% Body Predicates\n")
        for p in sorted(list(preds)): f.write(f"body_pred({p}).\n")
        
        f.write("\n%% Interpreted Background Knowledge & Helpers\n")
        f.write("empty([]).\nnot_empty([_|_]).\n")
        f.write("my_succ(A,B):- integer(A), (ground(B)->integer(B);true), succ(A,B).\n")
        f.write("my_prec(A,B):- integer(A), (ground(B)->integer(B);true), succ(B,A).\n")
        
        f.write("\n%% Metarules\n")
        f.write("metarule([P,Q,R], [P,A,B], [[Q,A,C],[R,C,B]]).\n")
        f.write("metarule([P,Q], [P,A,B], [[Q,A,B]]).\n")

        f.write("\n%% Background Knowledge\n")
        f.write("\n".join(bk) + "\n")

        f.write("\n%% Examples\n")
        f.write("\n".join(pos) + "\n")
        f.write("\n".join(neg) + "\n")

        f.write("\n%% Test Command\n")
        f.write("a :- learn(Pos, Neg). \n")
        
    print("Xong! File 1d_flip_metagol.pl đã chuẩn.")

if __name__ == "__main__":
    convert_to_metagol()