import overcooked_utils

env = overcooked_utils.create_overcooked_env()
obs, info = env.reset()
env.render(mode='human')
done = False
step = 0

while not done and step <= 1000:
    obs, reward, done, info = env.step(interactive=True)
    env.render(mode='human')
    step += 1