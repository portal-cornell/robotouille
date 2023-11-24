(define (problem robotouille)
(:domain robotouille)
(:objects
    table1 - station
    stove1 - station
    table2 - station
    table3 - station
    board1 - station
    table4 - station
    patty1 - item
    lettuce1 - item
    bottombun1 - item
    topbun1 - item
    robot1 - player
    robot2 - player
    robot3 - player
    robot4 - player
)
(:init
    (istable table1)
    (isstove stove1)
    (istable table2)
    (istable table3)
    (isboard board1)
    (istable table4)
    (ispatty patty1)
    (iscookable patty1)
    (islettuce lettuce1)
    (iscuttable lettuce1)
    (isbottombun bottombun1)
    (istopbun topbun1)
    (isrobot robot1)
    (isrobot robot2)
    (isrobot robot3)
    (isrobot robot4)
    (at patty1 table1)
    (loc robot1 table1)
    (empty stove1)
    (loc robot2 stove1)
    (at lettuce1 table2)
    (loc robot3 table2)
    (at bottombun1 table3)
    (vacant table3)
    (empty board1)
    (vacant board1)
    (at topbun1 table4)
    (loc robot4 table4)
    (nothing robot1)
    (nothing robot2)
    (nothing robot3)
    (nothing robot4)
    (selected robot1)
    (on patty1 table1)
    (clear patty1)
    (on lettuce1 table2)
    (clear lettuce1)
    (on bottombun1 table3)
    (clear bottombun1)
    (on topbun1 table4)
    (clear topbun1)
)
(:goal
   (or
       (and
           (iscut lettuce1)
           (atop topbun1 lettuce1)
           (iscooked patty1)
           (atop lettuce1 patty1)
           (atop patty1 bottombun1)
       )
   )
)
