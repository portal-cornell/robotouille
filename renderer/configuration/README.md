# Configuration File

Our goal for Robotouille is for it to be configurable so that users are able to use their own assets and customize the predicates to their liking. We have created a simple json for you to configure the game's assets.

## Configuring the Game Assets

### Description

There are four main types of objects in the game. Each object has a set of properties that can be configured. The features we currently support are:

- **Player**: changing the front, back, left and right image for the player
- **Floor**: changing the floor tilesets
- **Item**: changing universal scaling and offset constants, and adding items that can each have their own offset constant and multiple images with corresponding predicates
- **Station**: adding stations and their corresponding images

### Example Format

Here we describe the format of the JSON files under `configuration`.

```
{
    "version" = The current version of the configuration file

    "player" = A dictionary of player models that can be used in the game. Currently, Robotouille only supports setting a single set of assets to be used for all players.
    {
        "robot" = A dictionary of assets to draw the player model
        {
            "front" = The image for the front of the player
            "back" = The image for the back of the player
            "left" = The image of the player facing left
            "right" = The image of the player facing right
        }
    }

    "floor" = References to the tilings to be used for the ground and furniture
    {
        "ground" = List of tilings to be used for the ground
        "furniture" = List of tilings to be used for the furniture
    }

    "item" = The configuration for items in the game
    {
        "constants" = A dictionary of constants to be applied to all items
        {
            "STATION_ITEM_OFFSET" = How much higher or lower items should be rendered when placed on a station
            "X_SCALE_FACTOR" = How much items should be scaled in the x direction
            "Y_SCALE_FACTOR": How much items should be scaled in the y direction
        }
        "entities" = A dictionary of items that can be used in the game
        {
            "item_name1" = The name of the item
            {
                "assets" = A dictionary of images for the item
                {
                    "default" = The default image for the item
                    "item_state1" = The image for an item if certain predicates are true
                    {
                        "asset" = The image for the item when the predicates is true
                        "predicates" = A list of predicates that must be true for the image to be rendered
                    }
                    ...
                }
                "constants" = A dictionary of constants to be applied to the item
                {
                    "STACK_OFFSET" = How much higher or lower the item should be rendered when stacked
                }
            }
            ...
        }
    }
    "station" = The configuration for stations in the game
    {
        "entities" = A dictionary of stations that can be used in the game
        {
            "station_name1" = The name of the station
            {
                "assets" = A dictionary of images for the station. Currently, only one image is supported
                {
                    "default" = The default image for the station
                    "tile" = Stations can alternatively be given a tiling character which is rendered with the furniture tiling
                }
            }
        }
    }
}
```

### RobotouilleRenderer and RobotouilleCanvas

The `RobotouilleRenderer` class sets up the pygame window and reads the configuration file to use in `RobotouilleCanvas`. `RobotouilleCanvas` is responsible for drawing the images onto the window using the information from the configuration file.
