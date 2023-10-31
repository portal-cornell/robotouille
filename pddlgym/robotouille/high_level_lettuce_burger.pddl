(define (problem robotouille)
(:domain robotouille)
(:objects
    table1 - station
    table2 - station
    stove1 - station
    table3 - station
    table4 - station
    table5 - station
    board1 - station
    table6 - station
    table7 - station
    table8 - station
    patty1 - item
    cheese1 - item
    onion1 - item
    lettuce1 - item
    tomato1 - item
    chicken1 - item
    bottombun1 - item
    topbun1 - item
    robot1 - player
)
(:init
    (istable table1)
    (istable table2)
    (isstove stove1)
    (istable table3)
    (istable table4)
    (istable table5)
    (isboard board1)
    (istable table6)
    (istable table7)
    (istable table8)
    (ispatty patty1)
    (iscookable patty1)
    (ischeese cheese1)
    (isonion onion1)
    (iscuttable onion1)
    (islettuce lettuce1)
    (iscuttable lettuce1)
    (istomato tomato1)
    (iscuttable tomato1)
    (ischicken chicken1)
    (iscookable chicken1)
    (isbottombun bottombun1)
    (istopbun topbun1)
    (isrobot robot1)
    (at patty1 table1)
    (loc robot1 table1)
    (at cheese1 table2)
    (vacant table2)
    (empty stove1)
    (vacant stove1)
    (at onion1 table3)
    (vacant table3)
    (at lettuce1 table4)
    (vacant table4)
    (at tomato1 table5)
    (vacant table5)
    (empty board1)
    (vacant board1)
    (at chicken1 table6)
    (vacant table6)
    (at bottombun1 table7)
    (vacant table7)
    (at topbun1 table8)
    (vacant table8)
    (nothing robot1)
    (on patty1 table1)
    (clear patty1)
    (on cheese1 table2)
    (clear cheese1)
    (on onion1 table3)
    (clear onion1)
    (on lettuce1 table4)
    (clear lettuce1)
    (on tomato1 table5)
    (clear tomato1)
    (on chicken1 table6)
    (clear chicken1)
    (on bottombun1 table7)
    (clear bottombun1)
    (on topbun1 table8)
    (clear topbun1)
)
(:goal
   (or
       (and
           (iscut lettuce1)
           (iscooked patty1)
           (atop topbun1 lettuce1)
           (atop lettuce1 patty1)
           (atop patty1 bottombun1)
       )
   )
)
