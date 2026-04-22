door(d1).
door(d2).
cake(ls).

log(d1,1198).
log(d2,1204).
log(ls,1200).

log_r(X1, N) :- log(X1, N1), &split_number_naive(N1,20,10;N).

step(0..150).
time(X) :- step(Y), X = (1100+Y).

inRoom(X,T_1) :- time(T_1), door(X), log_r(X,T_2), T_2 <= T_1.
suspect(X) :- time(T), cake(C), inRoom(X,T_1), log_r(C,T_2), T_1 <= T_2.
nonUniqueSuspect(X) :- suspect(X), suspect(Y), X != Y.
culprit(X) :- suspect(X), not nonUniqueSuspect(X).
someoneInRoom(T) :- time(T), inRoom(X,T).
:- cake(C), log_r(C,T), not someoneInRoom(T).

#show suspect/1.