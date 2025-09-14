import subprocess

ALL_TESTS = {
    'synchronous':[
        '0_cheese_sandwich',
        '1_lettuce_sandwich',
        '2_lettuce_tomato_sandwich',
        '3_burger',
        '4_cheeseburger',
        '5_double_cheeseburger',
        '6_lettuce_tomato_cheeseburger',
        '7_two_lettuce_chicken_sandwich',
        '8_two_lettuce_tomato_burger',
        '9_onion_cheese_burger_and_lettuce_tomato_chicken_sandwich'
    ],
    'multi_agent':[
        '1_lettuce_burger',
        '2_lettuce_tomato_burger',
        '3_lettuce_fried_chicken_fried_onion_burger',
        '4_lettuce_chicken_sandwich',
        '5_lettuce_tomato_chicken_sandwich',
        '6_double_lettuce_chicken_burger',
        '7_onion_potato_tomato_soup',
        '8_tomato_cheeseburger_onion_chicken_sandwich',
        '9_two_lettuce_cheeseburger',
        '10_potato_tomato_chicken_soup_potato_cheese_onion_soup'
    ] 
}

for test_group, tests in ALL_TESTS.items():
    print(f"Running {test_group} tests")
    for test in tests:
        print(f"Running {test} test")
        subprocess.run(f"python main.py ++game.environment_name={test_group}/{test}", shell=True)
        print(f"Running {test} procedural generation test")
        subprocess.run(f"python main.py ++game.environment_name={test_group}/{test} ++game.seed=64", shell=True)
        print(f"{test} test successful\n")
    print(f"Finished running {test_group} tests\n")