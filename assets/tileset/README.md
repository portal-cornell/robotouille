# Tileset Assets

To ease the generation of beautiful tilings, Robotouille environments specify what type each tile on the map has. The renderer
does the work of calculating edges and corners to appropriately select the appropriate tile image from the tileset such that
transitions between different tile types are pleasing. To accommodate this functionality, tileset spritesheets must have an
associated JSON that describes the purpose of each tile in the spritesheet. This README details the format of this JSON.

## Tileset config.json

### Basic Information

The config JSON should have the following keys that describe basic properties of the tileset:

```
{
    "asset" = The filename of the spritesheet image
    "columns" = The number of columns in the spritesheet
    "rows" = The number of rows in the spritesheet

    ... (additional parts covered below)
}

```

### Letter Mappings

In addition, there is the entry `mappings` which describes to the renderer when to use the tiles in this tileset. This entry should contain an object whose keys are single letters. The tiling in an environment is specified as a character matrix, and the keys in this object specify which letters are handled by this spritesheet. Note that while the renderer supports using multiple spritesheets, each letter should appear in only one of those spritesheets to avoid conflict.

```
{
    ... (basic information)

    "mappings":
    {
        "C": [...]
        "W": [...]

        (this example JSON specifies that the spritesheet contains the imagery for "C" and "W" tiles)
    }
}
```

### Edge and Corner Mappings

For each letter in the `mappings` entry, a nested array structure informs the renderer which tiles to use when executing transitions between tile types. For aesthetic reasons, when a tile borders a tile of a different type, the tile image may show a border or transition at places of contact. The mapping information here describes which tile image to use depending on which parts of the tile are in contact with other types versus the same type.

The tile mappings start with an array of arrays. Each element array is a pair of a 4 character string and another array. The string consists of 4 numerals, each of corresponds to a cardinal direction. The numeral `0` indicates that the adjacent tile in that direction is of the same type as the current tile, whereas `1` indicates it is of a different type. The first numeral corresponds to North, the second to East, the third to South, and the fourth to West.

```
{
    ... (basic information)

    "mappings":
    {
        "C": [...]
        "W":
        [
            ["1100", [...]], ("1100" indicates there are a foreign tiles adjacent to the north and east edges)
            ["0001", [...]], ("0001" indicates there is a foreign tile adjacent to the west edge only)
            ...
        ]
    }
}
```

Looking into the array associated with an edge, this array is filled with arrays, each of which is a pair of a 4 character string (like before) and a number. The character string indicates which of the immediate corners has a foreign-typed tile. Like before, the numeral `0` indicates that the adjacent tile in that direction is of the same type as the current tile, whereas `1` indicates it is of a different type. The first numeral corresponds to North-East, the second to South-East, the third to South-West, and the fourth to North-West.

The number associated with the string specifies which sprite in the spritesheet corresponds to the associated edge and corner adjacencies. The numbering system is 1-indexed, starts in the top-left of the spritesheet, and moves right, wrapping to the row below after reaching the rightmost tile.

```
{
    ... (basic information)

    "mappings":
    {
        "C": [...]
        "W":
        [
            ["1100",
                [
                    ["0000", 16], ("0000" indicates there are no foreign tiles in the corners; the sprite numbered 16 should be drawn)
                    ["0010", 6] ("0010" indicates there is a foreign tile at the south-west corner; the tile numbered 6 should be drawn)
                ]
            ]
            ...
        ]
    }
}
```

Not every permutation of edge and corner adjacencies needs to be in the JSON. If a particular edge or corner string is not found in the JSON, then by default the value associated with `"0000"` will be chosen.

It should also be noted the renderer ignores corner information if the edge information makes it redundant. For example, if a tile has a foreign tile on its eastern edge, then the corner string used to lookup the tile sprite will have the eastern corners cleared (e.g. be in the form `"00??"`). This reduces redundancy since a border along the eastern edge already covers both eastern corners.
