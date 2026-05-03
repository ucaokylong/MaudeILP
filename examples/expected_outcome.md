## grandparent case
grandparent(A,B) :- father(A,C), father(C,B) .   grandparent(A,B) :- father(A,C), mother(C,B) .   grandparent(A,B) :- mother(A,C), father(C,B) .   grandparent(A,B) :- mother(A,C), mother(C,B) .


## graph-connectedness.maude
    target(A,B) :- edge(A,B) .   target(A,B) :- edge(A,C), edge(C,B) .   target(A,B) :- edge(A,C), target(C,B) .