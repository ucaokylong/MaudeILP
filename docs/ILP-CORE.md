# ILP-CORE: Canonical Maude Encoding for Metagol ILP Tasks

This document explains the `ILP-CORE` module: a common Maude encoding
used by all ILP / Metagol tasks in this project.

---

## 1. Goal of ILP-CORE

Metagol tasks are usually written in Prolog and have four main parts:

- background knowledge `B` (facts),
- positive examples `E+`,
- negative examples `E-`,
- a set of metarules `M`.

`ILP-CORE` defines a **generic vocabulary** (types and constructors)
so that any such task can be represented as *data* in Maude.

Each concrete task (grandparent, graph colouring, …):

- imports `ILP-CORE`, and
- instantiates four constants: `BK`, `POS`, `NEG`, `MRS`.

The learning engine (`METAGOL-ENGINE`) then works uniformly on these
structures, independent of the specific task.

---

## 2. The ILP-CORE module

```maude
fmod ILP-CORE is
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
endfm
```
This is a functional module (fmod), so it only defines data structures and functions, not transition rules.

### 2.1 Sorts: abstract ILP universe
```
sort PredName Const TermList Atom AtomList Metarule MRList .
```
PredName – predicate symbols with arityExamples: pred("mother",2), pred("grandparent",2).Const – Herbrand constantsExamples: const("ann"), const("amy"), const("green").TermList – list of arguments of a literalExample: const("ann") const("amy") encodes the tuple $(ann, amy)$.Atom – a ground literal $p(t_1, \dots, t_n)$ encoded as:atom(PredName, TermList).AtomList – list of atoms, used later to represent BK, POS, NEG.Metarule – one metarule at the data level.MRList – list of metarules.This gives us a uniform “ILP universe” inside Maude: every Prolog literal or metarule will be translated into one of these sorts.

