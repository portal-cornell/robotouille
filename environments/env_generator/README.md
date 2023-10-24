Please read the following to learn how to create a new environment for Robotouille.

Here we describe the format of the JSON files under `examples`.

```
{
    "width" = The width dimension of the environment (in tiles)
    "height" = The height dimension of the environment (in tiles)
    "stations" = A list of station objects in the environment
    [
        {
            "name" = The name of this station object
            "x" = The x position of this station relative to the bottom left origin
            "y" = The y position of this station relative to the bottom left origin
            "predicates" = A list of additional existing predicates to apply to this station
            "id" = (UNUSED) A custom string identifier to add to this station (for use in goal)
        },
        ...
    ],
    "items" = A list of item objects in the environment
    [
        {
            "name" = The name of this item object
            "x" = The x position of this item relative to the bottom left origin
            "y" = The y position of this item relative to the bottom left origin
            "stack-level" = The current position in this item in a stack (the lowest being 0)
            "predicates" = A list of additional existing predicates to apply to this item
            "id" = (UNUSED) A custom string identifier to add to this item (for use in goal)
        },
        ...
    ],
    "players" = A list of players in the environment (currently assumed to be one)
    [
        {
            "name" = The name of this player
            "x" = The x position of the player relative to the bottom left origin
            "y" = The y position of the player relative to the bottom left origin
            "direction" = A list of length two with the direction this player is facing
            "predicates" = A list of additional existing predicates to apply to this player
            "id" = (UNUSED) A custom string identifier to add to this player (for use in goal)
        },
        ...
    ],
    "goal description" = A string description of the goal in this environment
    "goal" = A high-level description of the goal in this environment.
    [
        {
            "predicate" = An existing predicate that is part of this environment's goal
            "args" = A list of arguments to the above predicate of objects in this environment
            "ids" = A list of IDs to distinguish the arguments. These can be integers (to denote uniqueness
            among similar objects e.g. patties in different hamburgers) or strings (to directly 
            distinguish between similar objects via usage of the "id" fields of objects e.g. the
            hamburger must be assembled on a specific table)
        },
        ...
    ]
}
```

While the schema for goals is described, it is currently not in use. The example JSONs may make use of the UNUSED
fields but this is to serve as examples of how a goal may be described. The actual goal of all environments is
currently (and (not(isrobot robot))) which is intentionally impossible to satisfy with the current PDDL domain
so that the environment doesn't terminate early.