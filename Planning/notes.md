
**pseudo code board.make_move()**

params: move
current, target
current type, target type

add moved

adjust piece lists
    friendly
    opponent
update square-centric list

update zobrist key
update fifty moves counter

switch player to move




**pseudo code board.reverse_move()**
params: move to reverse

switch player to move


**Board relative perspective**
|play as red|red moves first|Output|
|-----------|---------------|------|
|True|True|True|
|False|True|False|
|True|False|False|
|False|False|True|


**Truth Table is pst flipped**
is_red_up   is red moving   is board flipped
True        True            False
False       True            True
True        False           True
False       False           False

condition: is_red_up xor is red moving


**efficient attack data generation**

for each rook
min_dist = min(distx, disty)
if min_dist > 1 continue
get direction index
if min_dist == 1 generate attack ray
if not min_dist get cannon imposed limits

THIS IS BULLTSHIT FUCK


**Horse attack data optimization**
get_slope(d_1, d_2):
return d_2 / d_1

dists = get_dists(horse, friendly king)
mhd = sum(dists)
if mhd > 4: continue
slope = get_slope(*sorted(dist_x, dist_y))

if slope == 1 or slope == 3:
attack_map.add()



**Zobrist Hashing**
* for each piece for each square initialize random value
> How to get unique key
* iterate through piece lists, get random value for piece on square
* xor value into zobrist key
> How use keys
* set of zobrist keys
* create zobrist key for position
* if key is found, use stored values
    * if depth > stored depth use values
    * else update values
* else proceed with normal minimax
> Storing a Position
* zobrist key
* alpha, beta
* plies played

https://github.com/SebLague/Chess-AI/blob/main/Assets/Scripts/Core/TranspositionTable.cs
https://github.com/SebLague/Chess-AI/blob/main/Assets/Scripts/Core/AI/Search.cs


