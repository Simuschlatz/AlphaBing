
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


