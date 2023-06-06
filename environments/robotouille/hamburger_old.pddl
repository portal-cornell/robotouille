(define (problem robotouille)
    (:domain robotouille)
    (:objects 
        table1 - station
        table2 - station
        table3 - station
        table4 - station
        stove - station
        board - station
        robot - player
        topbun - item
        bottombun - item
        lettuce - item
        patty - item
    )
    (:init
        ; Identity inits
        (istable table1)
        (istable table2)
        (istable table3)
        (istable table4)
        (isstove stove)
        (isboard board)
        (isrobot robot)
        (istopbun topbun)
        (isbottombun bottombun)
        (islettuce lettuce)
        (iscuttable lettuce)
        (ispatty patty)
        (iscookable patty)
        
        ; State inits
        (loc robot stove)
        (at patty table1)
        (at lettuce table2)
        (at topbun table3)
        (at bottombun table4)
        (nothing robot)
        (empty stove)
        (empty board)
        (on patty table1)
        (on lettuce table2)
        (on topbun table3)
        (on bottombun table4)
        (vacant board)
        (vacant table1)
        (vacant table2)
        (vacant table3)
        (vacant table4)
        (clear patty)
        (clear lettuce)
        (clear topbun)
        (clear bottombun)
    )
    (:goal (and (iscut lettuce) (atop topbun lettuce) (iscooked patty) (atop lettuce patty) (atop patty bottombun)))
    ; TODO: Allow for disjunction goals such as the following which allows for the hamburger to be at either table3 or table4
    ; (:goal 
    ;     (or
    ;         (and (iscut lettuce) (at bun2 table3) (iscooked patty) (at lettuce table3) (at patty table3) (at bun1 table3))
    ;         (and (iscut lettuce) (at bun2 table4) (iscooked patty) (at lettuce table4) (at patty table4) (at bun1 table4))
    ;     )
    ; )
)
