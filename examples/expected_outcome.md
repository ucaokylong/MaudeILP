## grandparent.maude
grandparent(A,B) :- father(A,C), father(C,B) .
grandparent(A,B) :- father(A,C), mother(C,B) .
grandparent(A,B) :- mother(A,C), father(C,B) .
grandparent(A,B) :- mother(A,C), mother(C,B) .

## great-grandparent.maude
great-grandparent(A,B) :- parent(A,C) inv1(C,B) .
inv1(A,B) :- parent(A,C) parent(C,B) .

## graph-connectedness.maude
target(A,B) :- edge(A,B) .
target(A,B) :- edge(A,C), edge(C,B) .
target(A,B) :- edge(A,C), target(C,B) .