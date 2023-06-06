(define (problem robotouille)
(:domain robotouille)
(:objects
    table1 - station
    stove1 - station
    table2 - station
    table3 - station
    table4 - station
    board1 - station
    patty1 - item
    lettuce1 - item
    bottombun1 - item
    topbun1 - item
    robot1 - player
)
(:init
    (istable table1)
    (isstove stove1)
    (istable table2)
    (istable table3)
    (istable table4)
    (isboard board1)
    (ispatty patty1)
    (iscookable patty1)
    (islettuce lettuce1)
    (iscuttable lettuce1)
    (isbottombun bottombun1)
    (isbun bottombun1)
    (istopbun topbun1)
    (isbun topbun1)
    (isrobot robot1)
    (at patty1 table1)
    (vacant table1)
    (empty stove1)
    (loc robot1 stove1)
    (at lettuce1 table2)
    (vacant table2)
    (at bottombun1 table3)
    (vacant table3)
    (at topbun1 table4)
    (vacant table4)
    (empty board1)
    (vacant board1)
    (nothing robot1)
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
   (and
       (iscut lettuce1)
       (atop topbun1 lettuce1)
       (iscooked patty1)
       (atop lettuce1 patty1)
       (atop patty1 bottombun1)
   )
)
