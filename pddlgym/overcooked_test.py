import pddlgym
import overcooked_factory

# print("Literals")
# print(obs.literals)
# literal = next(iter(obs.literals))
# print(literal)
# print(type(literal))
# print("Objects")
# #print(obs.objects)
# print(type(obs.objects))
# print("Goal")
# #print(obs.goal)
# print(type(obs.goal))

def print_states(obs):
    print("Here is the current state:")
    states = obs.literals
    for state in states:
        print(f"- {state}")

def print_actions(env, obs):
    print("Here are the currently valid actions:")
    actions = list(env.action_space.all_ground_literals(obs))
    actions = sorted(actions, key=lambda x: str(x))
    for i, action in enumerate(actions):
        print(f"{i}) {action}")

def create_action(env, obs):
    action = ""
    valid_actions = list(env.action_space.all_ground_literals(obs))
    valid_actions = sorted(valid_actions, key=lambda x: str(x))
    while True:
        try:
            action = input()
            try:
                action = str(valid_actions[int(action)])
            except:
                pass
            action = overcooked_factory.str_to_literal(action)
            assert action in valid_actions
            break
        except ValueError:
            print(f"Your action [{action}] is malformatted. It must be in the form A(B:1,C:2,...)")
            continue
        except AssertionError:
            print(f"Your action [{action}] is invalid. Please choose from the list of valid actions.")
    return action

env = pddlgym.make("PDDLEnvOvercooked-v0")
obs, debug_info = env.reset()
#env.render(mode='human')
done = False
step = 0

while not done and step <= 1000:
    print('\n' * 10)
    if step % 10 == 0:
        print(f"You have made {step} steps. You have {1000-step} steps remaining.")
    print_states(obs)
    print('\n')
    print_actions(env, obs)
    action = create_action(env, obs)
    print(action)
    obs, reward, done, debug_info = env.step(action)
    #env.render(mode='human')

    step += 1