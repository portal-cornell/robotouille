#TODO: Automate this script

import subprocess

ALL_TESTS = {
    'base tests':[
        'base_add_to_soup',
        'base_boil_water',
        'base_cook',
        'base_cut',
        'base_fill_pot',
        'base_fill_two_pots',
        'base_move',
        'base_pickup_container',
        'base_pickup',
        'base_place_container',
        'base_place',
        'base_stack',
        'base_unstack'
    ],
    'composite tests':[
        'composite_add_fill_bowl',
        'composite_cook_pickup',
        'composite_cut_pickup',
        'composite_move_cook',
        'composite_move_cut',
        'composite_move_pickup',
        'composite_move_place',
        'composite_move_stack',
        'composite_move_unstack',
        'composite_place_cook',
        'composite_place_cut'
    ],
    'high level tests':[
        'cook_patties',
        'cook_soup',
        'cut_lettuces',
        'fry_chicken',
        'fry_potato',
        'high_level_assemble_burgers',
        'high_level_big_american_meal',
        'high_level_cheese_burger',
        'high_level_chicken_burger',
        'high_level_cook_and_cut',
        'high_level_lettuce_burger',
        'high_level_lettuce_tomato_burger',
        'high_level_two_cheese_burger',
        'high_level_two_chicken_burger',
        'high_level_two_lettuce_burger',
        'high_level_two_lettuce_tomato_burger',
        'kitchen',
        'original',
        'test_arena'
    ]
}

for test_group, tests in ALL_TESTS.items():
    print(f"Running {test_group} tests")
    for test in tests:
        print(f"Running {test} test")
        subprocess.run(f"python main.py ++game.environment_name {test}", shell=True)
    print(f"Finished running {test_group} tests\n")