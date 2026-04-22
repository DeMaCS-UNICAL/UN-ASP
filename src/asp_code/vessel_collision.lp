#uncertain vessel/4, 2. rho = 100, sigma = 100
#uncertain vessel/4, 3. rho = 100, sigma = 100

% --- Compute box limits (now in meters, using X/Y) ---
box_lat_min(V,T,MinY) :- vessel(V,_,Y,T), halfLat(V,HLat), MinY = Y - HLat.
box_lat_max(V,T,MaxY) :- vessel(V,_,Y,T), halfLat(V,HLat), MaxY = Y + HLat.

box_lon_min(V,T,MinX) :- vessel(V,X,_,T), halfLon(V,HLon), MinX = X - HLon.
box_lon_max(V,T,MaxX) :- vessel(V,X,_,T), halfLon(V,HLon), MaxX = X + HLon.

% --- Overlap in "latitude" axis (actually Y axis in meters) ---
lat_overlap(V1,V2,T) :- V1 < V2, box_lat_min(V1,T,Min1), box_lat_max(V1,T,Max1), box_lat_min(V2,T,Min2), box_lat_max(V2,T,Max2), Min1 <= Max2, Min2 <= Max1.

% --- Overlap in "longitude" axis (actually X axis in meters) ---
lon_overlap(V1,V2,T) :- V1 < V2, box_lon_min(V1,T,Min1), box_lon_max(V1,T,Max1), box_lon_min(V2,T,Min2), box_lon_max(V2,T,Max2), Min1 <= Max2, Min2 <= Max1.

% --- Box collision if both overlaps hold ---
box_collision(V1,V2,T) :- vessel(V1,_,_,T), vessel(V2,_,_,T), V1 < V2, lat_overlap(V1,V2,T), lon_overlap(V1,V2,T).

#show lat_overlap/3.
#show lon_overlap/3.
#show box_collision/3.

vessel(228051000, 38311, 42402, 1443650684).
vessel(228017700, 38265, 42375, 1443650684).
halfLon(228051000, 4). halfLat(228051000, 14).
halfLon(228017700, 5). halfLat(228017700, 22).