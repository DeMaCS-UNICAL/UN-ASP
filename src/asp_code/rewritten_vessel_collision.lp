vessel_r(X1, N, M, X4) :- vessel(X1, N1, M1, X4), &split_number_naive(N1,100,100;N), &split_number_naive(M1,100,100;M).

overlap(V1,V2) :- vessel_r(V1,X,Y,T), vessel_r(V2,X,Y,T), V1 != V2.

vessel(228051000,38311,42402,1443650684).
vessel(228017700,38265,42375,1443650684).
