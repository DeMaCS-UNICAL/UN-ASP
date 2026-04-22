door(d1).
door(d2).
cake(ls).

log(d1,1198).
log(d2,1204).
log(ls,1200).

#uncertain log/2, 2. rho=20, sigma=10

step(0..150).
time(X) :- step(Y), X = 1100 + Y.

inRoom(X,T_1) :- time(T_1), door(X), log(X,T_2), T_2 <= T_1.
suspect(X) :- time(T), cake(C), inRoom(X,T_1), log(C,T_2), T_1 <= T_2.
nonUniqueSuspect(X) :- suspect(X), suspect(Y), X != Y. 
culprit(X) :- suspect(X), not nonUniqueSuspect(X).
someoneInRoom(T) :- time(T), inRoom(X,T).
:- cake(C), log(C,T), not someoneInRoom(T).

#show suspect/1.