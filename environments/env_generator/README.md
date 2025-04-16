# Environment Generator

Our goal with Robotouille is to make it very easy to create new environments. We have created a simple JSON format for you to create your own environments. We also have built-in procedural generation to test your agents' robustness to new environments for a given goal. If you have any questions or ideas to make Robotouille more customizable, please create an issue or reach out to us!

## Creating Environments

### Description

The features we currently support are:

- Changing the width/height of the environment
- Adding various items and stations into the environment
    - See `object_enums.py` and `domain/robotouille.json` for the items and stations we support
    - For 'wildcard' items or stations, you can use the word 'item' or 'station' in your environment JSON
- Single and multiplayer
- Expressive goal descriptions

#### Goal Descriptions

We have a simple expressive language for describing goals in the environment. Consider the goal, "Make a lettuce burger". This requires a bottom bun, a lettuce burger, a patty, and a top bun. Ideally, we would describe this goal in PDDL as follows:

```
(:goal (and
    (on patty bottombun)
    (on lettuce patty)
    (on topbun lettuce)
))
```

but things get complicated when we have multiple types of the same ingredient. How do we express that the patty on the bottombun is the same patty that the lettuce is on? Or what if we would like these patties to be different? We resolve this by introducing IDs in our JSON to make this explicit. We also have support for IDs that require that a specific item must be used in a goal by using letters instead of numbers. Refer below for more details on the example format and under `examples` for various examples using the ID system.

### Example Format

Here we describe the format of the JSON files under `examples`.

```
{
    "width" = The width dimension of the environment (in tiles)
    "height" = The height dimension of the environment (in tiles)
    "config" = Configurable environment settings
    {
        "num_cuts" = The number of cuts that can be made on a single item
        {
            "item_name1": <NUM_CUTS>,
            "item_name2": <NUM_CUTS>,
            ...,
            "default: <NUM_CUTS>
        },
        "cook_time" = The number of steps it takes to cook an item
        {
            "item_name1": <COOK_TIME>,
            "item_name2": <COOK_TIME>,
            ...,
            "default: <COOK_TIME>
        }
    }
    "flooring" = (Optional) String matrix of ground tile types (see tileset README)
    "stations" = A list of station objects in the environment
    [
        {
            "name" = The name of this station object
            "x" = The x position of this station relative to the bottom left origin
            "y" = The y position of this station relative to the bottom left origin
            "predicates" = A list of additional existing predicates to apply to this station
            "id" = A custom string identifier to add to this station (for use in goal)
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
            "id" = A custom string identifier to add to this item (for use in goal)
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
            "id" = A custom string identifier to add to this player (for use in goal)
        },
        ...
    ],
    "goal description" = A string description of the goal in this environment
    "goal" = A high-level description of the goal in this environment.
    [
        {
            "predicate" = An existing predicate that is part of this environment's goal
            "args" = A list of arguments to the above predicate of objects in this environment
            "ids" = A list of IDs to distinguish the arguments. These can be integers (to denote uniqueness among similar objects e.g. patties in different hamburgers) or strings (to directly distinguish between similar objects via usage of the "id" fields of objects e.g. the hamburger must be assembled on a specific table)
        },
        ...
    ]
}
```

## Procedural Generation

We support procedural generation of environments given an environment JSON. When constructing an environment, we ensure that all stations are reachable by the robot and that all the stations and items specified in the JSON are present in the environment. It is assumed that the goal is achievable given the stations and items provided in the JSON - you can think of the environment JSONs as a way to specify the bare minimum stations and items necessary to achieve the goal.

Our procedural generation by default randomizes the location of items on stations and held by the player (note it also randomizes the position of the stations but due to the current lack of a distance metric this is only a rendering difference).

The procedural generation currently does not randomize the states of objects (an environment can start with cut letuce and/or cooked patties) nor does it randomize objects to be stacked upon one another.

We have a slightly easier procedural generation option, `noisy_randomization`, which ensures that while new items and stations can be generated, the state in which the JSON was defined is preserved. In other words, a sequence of actions that achieves the goal in the original JSON will also achieve the goal in the generated environment except that the arguments may be named differently (hence 'noisy' randomization). Thus, you would not need to deal with issues such as irrelevant items blocking stations you need to use, or relevant items being on the bottom of a stack of irrelevant items.
