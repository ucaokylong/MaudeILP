# MaudeILP-An Inductive Logic Programming system implemented in Maude.
This repository was created to implement the Inductive Logic Programming (ILP) algorithm **Metagol** in the **Maude** rewriting logic framework.   The project explores how the expressive power of *rewriting logic* can be used to represent, reason, and generalize hypotheses in ILP systems.

## ILP-CORE: Canonical Maude Encoding for Metagol ILP Tasks

This section explains how to encode a Metagol-style ILP task into a **canonical Maude representation** using the `ILP-CORE` module.

### 1. The ILP-CORE functional module

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
