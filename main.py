import robotouille_env
import robotouille_input
import argparse
import threading
import pygame

parser = argparse.ArgumentParser()
parser.add_argument("--environment_name", help="The name of the environment to create.", default="original")
parser.add_argument("--seed", help="The seed to use for the environment.", default=None, type=int)
args = parser.parse_args()

noisy_randomization = True
env, json, renderer = robotouille_env.create_robotouille_env(args.environment_name, args.seed, noisy_randomization)
obs, info = env.reset()
env.render(mode='human')
done_event = threading.Event()

# def step_fn(done_event: threading.Event):
#     while not done_event.is_set():
#         print(pygame.event.get())
#         pygame_events = filter(lambda e: e.type == KEYDOWN, pygame.event.get())
#         if pygame_events:
#             print(pygame_events)
#         if False:
#             obs, reward, done, info = env.step(interactive=True)
#             done_event.set() if done else done_event.clear()
#         pass

# step_thread = threading.Thread(target=step_fn, args=(pygame,done_event,))
# step_thread.start()

while not done_event.is_set():
    pygame_events = pygame.event.get()
    mousedown_events = list(filter(lambda e: e.type == pygame.MOUSEBUTTONDOWN, pygame_events))
    keydown_events = list(filter(lambda e: e.type == pygame.KEYDOWN, pygame_events))
    # if mousedown_events:
    #     print(mousedown_events)
    #     print(pygame_events)
    # if keydown_events:
    #     print(keydown_events)
    #     print(pygame_events)
    #     # Check if the user pressed the E key
    #     if keydown_events[0].key == pygame.K_e:
    #         print("pressed E")
    action = robotouille_input.create_action_from_control(env, obs, mousedown_events+keydown_events, renderer)
    obs, reward, done, info = env.step(action=action)
    done_event.set() if done else done_event.clear()
    env.render(mode='human')

# step_thread.join()