import re
from pathlib import Path

def parse_pred_decl(line):
    m = re.match(r'\s*body_pred\((\w+)/(\d+)\)\s*\.\s*', line)
    if not m:
        return None
    name, arity = m.group(1), int(m.group(2))
    return name, arity

def parse_literal_core(s):
    m = re.match(r'\s*(\w+)\s*\(([^()]*)\)\s*', s)
    if not m:
        return None
    pred = m.group(1)
    args_str = m.group(2).strip()
    if args_str == "":
        args = []
    else:
        args = [a.strip() for a in args_str.split(",") if a.strip() != ""]
    return pred, args

def parse_fact(line):
    stripped = line.strip()
    if not stripped.endswith("."):
        return None
    core = stripped[:-1]
    return parse_literal_core(core)

def parse_metarule(line):
    m = re.match(r'\s*metarule\((.*)\)\s*\.\s*', line)
    if not m:
        return None
    inner = m.group(1).strip()
    return inner

def parse_examples_block(block_str):
    # block_str chứa kiểu:
    # Pos = [
    #   grandparent(ann,amelia),
    #   ...
    # ],
    # Bóc phần trong [ ... ] rồi đọc từng dòng có chứa ')'
    inside = re.search(r'\[(.*)\]', block_str, re.S)
    if not inside:
        return []
    content = inside.group(1)
    atoms = []
    for line in content.splitlines():
        line = line.strip()
        if line == "" or line in {",", "]"}:
            continue
        # bỏ dấu phẩy cuối dòng nếu có
        if line.endswith(","):
            line = line[:-1]
        lit = parse_literal_core(line)
        if lit:
            atoms.append(lit)
    return atoms

def convert_metagol_file(in_path: Path, module_name: str, out_path: Path):
    text = in_path.read_text()

    lines_no_comments = []
    for line in text.splitlines():
        line = line.split('%', 1)[0]
        if line.strip() == "":
            continue
        lines_no_comments.append(line)
    cleaned = "\n".join(lines_no_comments)

    pos_block = re.search(r'Pos\s*=\s*\[(.*?)\]', cleaned, re.S)
    neg_block = re.search(r'Neg\s*=\s*\[(.*?)\]', cleaned, re.S)
    pos_atoms = parse_examples_block(pos_block.group(0)) if pos_block else []
    neg_atoms = parse_examples_block(neg_block.group(0)) if neg_block else []

    print("DEBUG Pos block:", bool(pos_block), "Neg block:", bool(neg_block))
    print("DEBUG #Pos:", len(pos_atoms), "#Neg:", len(neg_atoms))

    preds = {}
    facts = []
    metarules = []

    for line in cleaned.splitlines():
        stripped = line.strip()

        if stripped.startswith(":-"):
            continue
        if "use_module" in line:
            continue
        if "learn(" in line:
            continue

        if "body_pred" in line:
            pd = parse_pred_decl(line)
            if pd:
                name, arity = pd
                preds[name] = arity
            continue

        if stripped.startswith("metarule"):
            mr = parse_metarule(line)
            if mr:
                metarules.append(mr)
            continue

        ft = parse_fact(line)
        if ft:
            facts.append(ft)
            continue

    facts     = [(p,as_) for (p,as_) in facts     if p != "learn"]
    pos_atoms = [(p,as_) for (p,as_) in pos_atoms if p != "learn"]
    neg_atoms = [(p,as_) for (p,as_) in neg_atoms if p != "learn"]

    def termlist(args):
        if not args:
            return "nilT"
        parts = " ".join(f'const("{a}")' for a in args)
        return parts

    def atom_to_maude(pred, args):
        arity = preds.get(pred, len(args))
        return f'    atom(pred("{pred}",{arity}), {termlist(args)})'

    bk_str  = "\n".join(atom_to_maude(p,as_) for (p,as_) in facts)     or "    nilA"
    pos_str = "\n".join(atom_to_maude(p,as_) for (p,as_) in pos_atoms) or "    nilA"
    neg_str = "\n".join(atom_to_maude(p,as_) for (p,as_) in neg_atoms) or "    nilA"
    mr_str  = "\n".join(f'    metarule("{m}")' for m in metarules)     or "    nilM"

    maude = f"""fmod {module_name} is
  sort PredName Const TermList Atom AtomList Metarule MRList .

  subsort Atom < AtomList .
  subsort Metarule < MRList .

  op nilA : -> AtomList [ctor] .
  op __   : AtomList AtomList -> AtomList [assoc id: nilA] .

  op nilM : -> MRList [ctor] .
  op __   : MRList MRList -> MRList [assoc id: nilM] .

  op nilT : -> TermList [ctor] .
  op __   : TermList TermList -> TermList [assoc id: nilT] .

  op pred  : String Nat -> PredName [ctor] .
  op const : String      -> Const    [ctor] .

  op atom  : PredName TermList -> Atom [ctor] .

  op metarule : String -> Metarule [ctor] .

  op BK  : -> AtomList .
  op POS : -> AtomList .
  op NEG : -> AtomList .
  op MRS : -> MRList .

  eq BK =
{bk_str}
  .

  eq MRS =
{mr_str}
  .

  eq POS =
{pos_str}
  .

  eq NEG =
{neg_str}
  .
endfm
"""
    out_path.write_text(maude)

if __name__ == "__main__":
    in_file  = Path("graph-colouring.pl")
    out_file = Path("ILP-graph-colouring.maude")
    convert_metagol_file(in_file, "ILP-graph-colouring", out_file)
