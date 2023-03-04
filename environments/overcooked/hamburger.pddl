(define (problem overcooked)
    (:domain overcooked)
    (:objects 
        table1 - station
        table2 - station
        table3 - station
        table4 - station
        stove - station
        board - station
        chef - player
        bun1 - item
        bun2 - item
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
        (isbun bun1)
        (isbun bun2)
        (islettuce lettuce)
        (iscuttable lettuce)
        (ispatty patty)
        (iscookable patty)
        
        ; State inits
        (loc chef stove)
        (at patty table1)
        (at lettuce table2)
        (at bun1 table3)
        (at bun2 table4)
        (nothing chef)
        (empty stove)
        (empty board)
        (on patty table1)
        (on lettuce table2)
        (on bun1 table3)
        (on bun2 table4)
        (vacant board)
        (vacant table1)
        (vacant table2)
        (vacant table3)
        (vacant table4)
        (clear patty)
        (clear lettuce)
        (clear bun1)
        (clear bun2)
    )
    ;(:goal (and (iscut lettuce) (atop bun2 lettuce) (iscooked patty) (atop lettuce patty) (atop patty bun1)))
    (:goal (and (iscut lettuce) (at bun2 table3) (iscooked patty) (at lettuce table3) (at patty table3) (at bun1 table3)))
)
