vessel_r(X1, N, M, X4) :- vessel(X1, N1, M1, X4), &split_number_naive(N1,1000,10;N), &split_number_naive(M1,100,10;M).

% --- Compute box limits (now in meters, using X/Y) ---
box_lat_min(V,T,MinY) :- vessel_r(V,_,Y,T), halfLat(V,HLat), MinY = (Y-HLat).
box_lat_max(V,T,MaxY) :- vessel_r(V,_,Y,T), halfLat(V,HLat), MaxY = (Y+HLat).

box_lon_min(V,T,MinX) :- vessel_r(V,X,_,T), halfLon(V,HLon), MinX = (X-HLon).
box_lon_max(V,T,MaxX) :- vessel_r(V,X,_,T), halfLon(V,HLon), MaxX = (X+HLon).

% --- Overlap in "latitude" axis (actually Y axis in meters) ---
lat_overlap(V1,V2,T) :- V1 < V2, box_lat_min(V1,T,Min1), box_lat_max(V1,T,Max1), box_lat_min(V2,T,Min2), box_lat_max(V2,T,Max2), Min1 <= Max2, Min2 <= Max1.

% --- Overlap in "longitude" axis (actually X axis in meters) ---
lon_overlap(V1,V2,T) :- V1 < V2, box_lon_min(V1,T,Min1), box_lon_max(V1,T,Max1), box_lon_min(V2,T,Min2), box_lon_max(V2,T,Max2), Min1 <= Max2, Min2 <= Max1.

% --- Box collision if both overlaps hold ---
box_collision(V1,V2,T) :- vessel_r(V1,_,_,T), vessel_r(V2,_,_,T), V1 < V2, lat_overlap(V1,V2,T), lon_overlap(V1,V2,T).

#show lat_overlap/3.
#show lon_overlap/3.
#show box_collision/3.
