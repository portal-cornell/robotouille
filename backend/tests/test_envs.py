#TODO: Automate this script

import subprocess
from collections import defaultdict

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
    # 'high level tests':[
    #     'cook_patties',
    #     'cook_soup',
    #     'cut_lettuces',
    #     'fry_chicken',
    #     'fry_potato',
    #     'high_level_assemble_burgers',
    #     'high_level_big_american_meal',
    #     'high_level_cheese_burger',
    #     'high_level_chicken_burger',
    #     'high_level_cook_and_cut',
    #     'high_level_lettuce_burger',
    #     'high_level_lettuce_tomato_burger',
    #     'high_level_two_cheese_burger',
    #     'high_level_two_chicken_burger',
    #     'high_level_two_lettuce_burger',
    #     'high_level_two_lettuce_tomato_burger',
    #     'kitchen',
    #     'original',
    #     'test_arena'
    # ],
    # "synchronous tests":[
    #     "synchronous/0_cheese_sandwich",
    #     "synchronous/1_lettuce_sandwich",
    #     "synchronous/2_lettuce_tomato_sandwich",
    #     "synchronous/3_burger",
    #     "synchronous/4_cheeseburger",
    #     "synchronous/5_double_cheeseburger",
    #     "synchronous/6_lettuce_tomato_cheeseburger",
    #     "synchronous/7_two_lettuce_chicken_sandwich",
    #     "synchronous/8_two_lettuce_tomatao_burger",
    #     "synchronous/9_onion_cheese_burger_and_lettuce_tomato_chicken_sandwich"
    # ]
}

def run():
    tallies = defaultdict(lambda: {"passed": 0, "failed": 0})
    overall = {"passed": 0, "failed": 0}
    failed_tests_detail = []

    try:
        for test_group, tests in ALL_TESTS.items():
            print(f"Running {test_group} tests")
            for test in tests:
                print(f"Running {test} test")
                result = subprocess.run(
                    f"python main.py ++game.environment_name={test}",
                    shell=True
                )
                if result.returncode == 0:
                    tallies[test_group]["passed"] += 1
                    overall["passed"] += 1
                else:
                    tallies[test_group]["failed"] += 1
                    overall["failed"] += 1
                    failed_tests_detail.append((test_group, test))
            print(f"Finished running {test_group} tests\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Printing partial results...\n")

    # ---- Summary per group ----
    print("\n==================== TEST SUMMARY ====================")
    for group, t in tallies.items():
        total = t["passed"] + t["failed"]
        if total == 0:
            continue
        print(f"{group}: {t['passed']} passed, {t['failed']} failed (total {total})")

    # ---- Overall summary ----
    grand_total = overall["passed"] + overall["failed"]
    print("------------------------------------------------------")
    print(f"OVERALL: {overall['passed']} passed, {overall['failed']} failed (total {grand_total})")

    # ---- List failed tests (if any) ----
    if failed_tests_detail:
        print("\nFailed tests:")
        for grp, tst in failed_tests_detail:
            print(f"  - [{grp}] {tst}")
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    run()