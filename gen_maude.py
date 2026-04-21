import re
import os

def safe_name(c):
    # Thêm chữ 'v' trước số để tránh lỗi 'ops 0'
    # Đổi '_' thành '-' để tránh lỗi Mixfix Operator
    if c.isdigit():
        return f"v{c}"
    return c.replace('_', '-')

def parse_line(line):
    line = line.strip()
    if not line or line.startswith(('%', ':-')): 
        return None
    
    # Bóc POS/NEG
    m_ex = re.match(r'^(pos|neg)\((.*)\)\.$', line)
    if m_ex:
        ex_type = m_ex.group(1)
        inner = m_ex.group(2)
        m_inner = re.match(r'^(\w+)\((.*)\)$', inner)
        if m_inner:
            pred = safe_name(m_inner.group(1))
            args = [safe_name(a.strip()) for a in m_inner.group(2).split(',')]
            return (ex_type, pred, args)
        return None
        
    # Bóc BK
    m_fact = re.match(r'^(\w+)\((.*)\)\.$', line)
    if m_fact:
        pred = safe_name(m_fact.group(1))
        args = [safe_name(a.strip()) for a in m_fact.group(2).split(',')]
        return ('bk', pred, args)
        
    return None

def convert_to_maude():
    constants = set()
    preds = {} # name -> arity
    bk, pos, neg = [], [], []

    for file in ['bk.pl', 'exs.pl']:
        if not os.path.exists(file): continue
        with open(file, 'r') as f:
            for line in f:
                res = parse_line(line)
                if res:
                    type_, pred, args = res
                    preds[pred] = len(args)
                    constants.update(args)
                    if type_ == 'pos': pos.append((pred, args))
                    elif type_ == 'neg': neg.append((pred, args))
                    else: bk.append((pred, args))

    with open('1d_flip_case.maude', 'w') as f:
        f.write("load ILP-CORE-ENGINE.maude\n\n")
        f.write("fmod 1D-FLIP-CASE is\n")
        f.write("  protecting ILP-SEARCH .\n\n")
        
        f.write("  --- CONSTANTS\n")
        sorted_consts = sorted(list(constants))
        # Khai báo hằng số (chia mỗi dòng 15 cái cho dễ nhìn)
        for i in range(0, len(sorted_consts), 15):
            chunk = sorted_consts[i:i+15]
            f.write(f"  ops {' '.join(chunk)} : -> Entity [ctor] .\n")
        
        f.write("\n  --- PREDICATES\n")
        for p, arity in preds.items():
            args_type = " ".join(["Entity"] * arity)
            f.write(f"  op {p} : {args_type} -> Pred [ctor] .\n")
        
        # GHI BK (Chuẩn format Grandparent: chỉ xuống dòng)
        f.write("\n  eq BK =\n")
        for p, a in bk:
            f.write(f"    {p}({', '.join(a)})\n")
        f.write("    .\n")

        # GHI POS (Chuẩn format Grandparent)
        f.write("\n  eq POS =\n")
        for p, a in pos:
            f.write(f"    {p}({', '.join(a)})\n")
        f.write("    .\n")

        # GHI NEG (Chuẩn format Grandparent)
        f.write("\n  eq NEG =\n")
        for p, a in neg:
            f.write(f"    {p}({', '.join(a)})\n")
        f.write("    .\n")

        # METARULES CẬP NHẬT: Hỗ trợ Arity 3 (Biến E)
        f.write("\n  var P Q R : Pred .\n  var E A B C D : Entity .\n")
        f.write("  eq METARULES =\n")
        f.write("    metarule([P | Q], [P : E,A,B], [Q : E,A,B])\n")
        f.write("    metarule([P | Q | R], [P : E,A,B], [Q : E,A,C] [R : E,C,B]) [nonexec]\n")
        f.write("    metarule([P | Q | R], [P : E,A,B], [Q : E,A,C] [R : C,B]) [nonexec] .\n\n")
        f.write("endfm\n")
    
    print("Xong! File 1d_flip_case.maude đã chuẩn 100% format Grandparent.")

if __name__ == "__main__":
    convert_to_maude()