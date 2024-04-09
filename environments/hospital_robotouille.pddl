;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;           Robotouille!!!          ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain robotouille)
    (:requirements :strips :typing :disjunctive-preconditions)
    (:types station player item)
    (:predicates
        ; Identity Predicates
        (istable ?s - station)
        (isstove ?s - station)
        (isboard ?s - station)
        (ispatient ?s - station)
        (istreatable ?i - station)
        (istreated ?i - station)    
        (isrobot ?p - player)
        (isnurse ?p - player)
        (istopbun ?i - item)
        (isbottombun ?i - item)
        (isbread ?i - item)
        (islettuce ?i - item)
        (isonion ?i - item)
        (istomato ?i - item)
        (iscuttable ?i - item)
        (iscut ?i - item)
        (ispatty ?i - item)
        (ischicken ?i - item)
        (iscookable ?i - item)
        (isingestable ?i - item)
        (isingested ?i - item)
        (iscooked ?i - item)
        (ispulsechecker ?i - item)
        (ischeese ?i - item)
        (ismedicine ?i - item)
        ; State Predicates
        (loc ?p - player ?s - station)
        (at ?i - item ?s - station)
        (nothing ?p - player)
        (empty ?s - station)
        (on ?i - item ?s - station)
        (vacant ?s - station)
        (clear ?i - item)
        (atop ?i1 - item ?i2 - item)
        (has ?p - player ?i - item)
        (selected ?p - player)
        (cancook ?p - player)
        (cancut ?p - player)
        (canmoveitem ?p - player)
        (canmove ?p - player)
        (canfry ?p - player)
        (canfrycut ?p - player)
    )

    ; ACTIONS

     ; Make the nurse player place a medicine item on top the patient station
    (:action givemedicine
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and
            (ispatient ?s)
            (isingestable ?i)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
        )
        :effect (and
            (istreated ?s)
        )
    ) 
    ; Move the player from station 1 to station 2
    (:action move
        :parameters (?p - player ?s1 - station ?s2 - station)
        :precondition (and
            (loc ?p ?s1)
            (selected ?p)
            (canmove ?p)
        )
        :effect (and
            (loc ?p ?s2)
            (vacant ?s1)
            (not (loc ?p ?s1))
            (not (vacant ?s2))
        )
    )

    ; Make the player pick up an item from a station
    (:action pick-up
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and 
            (nothing ?p)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
            (selected ?p)
            (canmoveitem ?p)
        )
        :effect (and 
            (has ?p ?i)
            (empty ?s)
            (not (nothing ?p))
            (not (at ?i ?s))
            (not (clear ?i))
            (not (on ?i ?s))
        )
    )

    ; Make the player place an item on a station
    (:action place
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and 
            (has ?p ?i)
            (loc ?p ?s)
            (empty ?s)
            (selected ?p)
            (canmoveitem ?p)
        )
        :effect (and 
            (nothing ?p)
            (at ?i ?s)
            (clear ?i)
            (on ?i ?s)
            (not (has ?p ?i))
            (not (empty ?s))
        )
    )

    ; Make the player cook a cookable item on a stove
    (:action cook
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and
            (isstove ?s)
            (iscookable ?i)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
            (selected ?p)
            (cancook ?p)
        )
        :effect (and 
            (iscooked ?i)
        )
    )

    ; Make the player fry a fryable item in a fryer
    (:action fry
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and
            (isfryer ?s)
            (isfryable ?i)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
            (selected ?p)
            (canfry ?p)
        )
        :effect (and 
            (isfried ?i)
        )
    )

    ; Make the player fry an item that is only fryable if cut, in a fryer
    (:action fry_cut_item
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and
            (isfryer ?s)
            (isfryableifcut ?i)
            (iscut ?i)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
            (selected ?p)
            (canfrycut ?p)
        )
        :effect (and 
            (isfried ?i)
        )
    )

    ; Make the player stack an item on top of another item at a station
    (:action stack
        :parameters (?p - player ?i1 - item ?i2 - item ?s - station)
        :precondition (and
            (has ?p ?i1)
            (clear ?i2)
            (loc ?p ?s)
            (at ?i2 ?s)
            (selected ?p)
            (canmoveitem ?p)
        )
        :effect (and
            (nothing ?p)
            (at ?i1 ?s)
            (atop ?i1 ?i2)
            (clear ?i1)
            (not (clear ?i2))
            (not (has ?p ?i1))
        )
    )    

    ; Make the player cut a cuttable item on a cutting board
    (:action cut
        :parameters (?p - player ?i - item ?s - station)
        :precondition (and
            (isboard ?s)
            (iscuttable ?i)
            (on ?i ?s)
            (loc ?p ?s)
            (clear ?i)
            (selected ?p)
            (cancut ?p)
        )
        :effect (and 
            (iscut ?i)
        )
    )

    ; Make the player unstack an item from another item at a station
    (:action unstack
        :parameters (?p - player ?i1 - item ?i2 - item ?s - station)
        :precondition (and 
            (nothing ?p)
            (clear ?i1)
            (atop ?i1 ?i2)
            (loc ?p ?s)
            (at ?i1 ?s)
            (at ?i2 ?s)
            (selected ?p)
            (canmoveitem ?p)
        )
        :effect (and 
            (has ?p ?i1)
            (clear ?i2)
            (not (nothing ?p))
            (not (clear ?i1))
            (not (atop ?i1 ?i2))
            (not (at ?i1 ?s))
        )
    )

    ; Change player selection
    (:action select
        :parameters (?p1 - player ?p2 - player)
        :precondition (and 
            (selected ?p1)
            (not  (selected ?p2))
        )
        :effect (and 
            (not (selected ?p1))
            (selected ?p2)
        )
    )

    
)