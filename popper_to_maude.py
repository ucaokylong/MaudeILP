import re

def generate_maude_ilp():
    bias_file = '/Users/ucaokylong/JAIST/Popper/examples/zendo1/bias.pl'
    bk_file = '/Users/ucaokylong/JAIST/Popper/examples/zendo1/bk.pl'
    exs_file = '/Users/ucaokylong/JAIST/Popper/examples/zendo1/exs.pl'
    out_file = '/Users/ucaokylong/JAIST/maude/MaudeILP/examples/zendo.maude'

    # Regex patterns
    type_re = re.compile(r"type\((\w+),\(([^)]*)\)\)\.")
    fact_re = re.compile(r"(\w+)\(([^)]+)\)\.")
    pos_re = re.compile(r"pos\((\w+)\(([^)]+)\)\)\.")
    neg_re = re.compile(r"neg\((\w+)\(([^)]+)\)\)\.")

    pred_signatures = {}
    states, pieces, numvals = set(), set(), set()
    bk_facts, pos_facts, neg_facts = [], [], []

    # 1. Parse Bias.pl để lấy chính xác Arity và Type
    with open(bias_file, 'r') as f:
        for line in f:
            m = type_re.search(line)
            if m:
                pred = m.group(1)
                raw_types = [t.strip() for t in m.group(2).split(',') if t.strip()]
                mapped_types = []
                for t in raw_types:
                    if t == 'real': mapped_types.append('NumVal')
                    elif t == 'state': mapped_types.append('State')
                    elif t == 'piece': mapped_types.append('Piece')
                    else: mapped_types.append(t.capitalize())
                pred_signatures[pred] = mapped_types

    # Định dạng biến an toàn tuyệt đối (Đã xử lý dấu gạch dưới và dấu âm)
    def format_arg(val, sort_type):
        val = val.strip()
        # FIX: Chuyển '_' thành 'x', chuyển '-' thành 'm'
        val = val.replace('_', 'x').replace('-', 'm')
        
        if sort_type == 'State':
            st = f"st{val}"
            states.add(st)
            return st
        elif sort_type == 'NumVal':
            n = f"n{val}"
            numvals.add(n)
            return n
        elif sort_type == 'Piece':
            pieces.add(val)
            return val
        return val

    # 2. Parse BK.pl (Quét sạch sẽ không bỏ sót)
    with open(bk_file, 'r') as f:
        for line in f:
            if line.startswith(":-") or not line.strip(): continue
            m = fact_re.search(line)
            if m:
                pred = m.group(1)
                args = [arg.strip() for arg in m.group(2).split(',')]
                if pred in pred_signatures:
                    types = pred_signatures[pred]
                    f_args = [format_arg(a, t) for a, t in zip(args, types)]
                    bk_facts.append(f"{pred}({', '.join(f_args)})")
                else:
                    print(f"CẢNH BÁO: Bỏ qua fact do không có trong bias.pl: {line.strip()}")

    # 3. Parse Exs.pl
    with open(exs_file, 'r') as f:
        for line in f:
            pos_m = pos_re.search(line)
            neg_m = neg_re.search(line)
            if pos_m:
                pred = pos_m.group(1)
                args = [arg.strip() for arg in pos_m.group(2).split(',')]
                f_args = [format_arg(a, pred_signatures[pred][i]) for i, a in enumerate(args)]
                pos_facts.append(f"{pred}({', '.join(f_args)})")
            elif neg_m:
                pred = neg_m.group(1)
                args = [arg.strip() for arg in neg_m.group(2).split(',')]
                f_args = [format_arg(a, pred_signatures[pred][i]) for i, a in enumerate(args)]
                neg_facts.append(f"{pred}({', '.join(f_args)})")

    # Hàm in chunk
    def get_chunked_ops(items, sort_name, chunk_size=10):
        lst = sorted(list(items))
        chunks = [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
        return "\n".join([f"    ops {' '.join(chunk)} : -> {sort_name} [ctor] ." for chunk in chunks])

    # 4. Ghi ra file Maude
    with open(out_file, 'w') as f:
        f.write("load ../MaudeILP.maude .\n\n")
        f.write("fmod ILP-PROBLEM is\n")
        f.write("    pr ILP-DEFINITION-INPUT .\n\n")
        
        # Sort Declarations
        f.write("    sorts State Piece NumVal .\n")
        f.write("    subsorts State Piece NumVal < Param .\n\n")

        # Constant Declarations
        f.write("    --- Constants for States\n")
        f.write(get_chunked_ops(states, "State", 12) + "\n\n")
        
        f.write("    --- Constants for Pieces\n")
        f.write(get_chunked_ops(pieces, "Piece", 10) + "\n\n")

        f.write("    --- Constants for Numbers\n")
        f.write(get_chunked_ops(numvals, "NumVal", 12) + "\n\n")

        # Predicate Declarations
        f.write("    --- Predicate Declarations\n")
        for pred, types in pred_signatures.items():
            if types:
                f.write(f"    op {pred} : {' '.join(types)} -> Pred [ctor] .\n")

        # Facts (BK, POS, NEG)
        f.write("\n    eq BK =\n        ")
        f.write("\n        ".join(bk_facts) + " .\n")
        
        f.write("\n    eq POS =\n        ")
        f.write("\n        ".join(pos_facts) + " .\n")

        f.write("\n    eq NEG =\n        ")
        f.write("\n        ".join(neg_facts) + " .\n")

        # ==========================================
        # 3 METARULES ĐƯỢC CHỌN LỌC
        # ==========================================
        f.write("\n    --- Selected Metarules for Zendo\n")
        f.write("    vars P Q R : Pred .\n")
        f.write("    vars A B C : Param .\n\n")
        
        f.write("    eq METARULES =\n")
        f.write("        --- 1. Projection (Sinh Target 1-ary từ Binary relation)\n")
        f.write("        (P(A)   :- (Q(A,B)) (R(B)))\n")
        f.write("        --- 2. Monadic Filter / Conjunction (Gộp 2 tính chất)\n")
        f.write("        (P(A)   :- (Q(A)) (R(A)))\n")
        f.write("        --- 3. Chain (Liên kết các thuộc tính 2-ary nếu cần)\n")
        f.write("        (P(A,B) :- (Q(A,C)) (R(C,B)))\n")
        f.write("        [nonexec] .\n")
        
        f.write("endfm\n\n")
        f.write("select MAUDE-ILP .\n")
        
        # Gọi depth = 4 vì rule đích của Zendo rất dài, cần invention lồng sâu
        f.write("--- Depth bound needs to be high enough for 5-body literal induction\n")
        f.write("red learn(4) .\n")

    print(f"✅ Conversion complete! Đã loại bỏ an toàn dấu '_' và '-'.")

if __name__ == "__main__":
    generate_maude_ilp()