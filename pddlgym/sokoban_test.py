#import matplotlib; matplotlib.use('agg')
import matplotlib.pyplot as plt
import pddlgym
import imageio

env = pddlgym.make("PDDLEnvSokoban-v0")
obs, debug_info = env.reset()
# images = [env.render('human')]
done = False
step = 0
actions = list(env.action_space.all_ground_literals(obs))

def collect_actions(actions):
    for action in actions:
        str_repr = str(action)
        if str_repr == "move(dir-down:direction)":
            down = action
        elif str_repr == "move(dir-left:direction)":
            left = action
        elif str_repr == "move(dir-right:direction)":
            right = action
        elif str_repr == "move(dir-up:direction)":
            up = action
    return up, left, down, right

def perform_action(wasd, action):
    if action == 'w':
        return wasd[0]
    elif action == 'a':
        return wasd[1]
    elif action == 's':
        return wasd[2]
    elif action == 'd':
        return wasd[3]
    return None

wasd = collect_actions(actions)

plt.ion()
fig, ax = plt.subplots()

img = env.render('human_crisp')
ax_img = ax.imshow(img)
fig.canvas.flush_events()

while not done and step <= 1000:
    if step % 10 == 0:
        print("Step", step)
    action = env.action_space.sample(obs)
    action = perform_action(wasd, input())
    obs, reward, done, debug_info = env.step(action)
    
    img = env.render('human_crisp')
    ax_img = ax.imshow(img)
    fig.canvas.flush_events()
    
    step += 1
#imageio.mimwrite('sokoban.mp4', images, fps=3)


# IMAGE_SIZE = 500
# import numpy as np
# import matplotlib.pyplot as plt


# plt.ion()

# fig1, ax1 = plt.subplots()
# fig2, ax2 = plt.subplots()
# fig3, ax3 = plt.subplots()

# # this example doesn't work because array only contains zeroes
# array = np.zeros(shape=(IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
# axim1 = ax1.imshow(array)

# # In order to solve this, one needs to set the color scale with vmin/vman
# # I found this, thanks to @jettero's comment.
# array = np.zeros(shape=(IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
# axim2 = ax2.imshow(array, vmin=0, vmax=99)

# # alternatively this process can be automated from the data
# array[0, 0] = 99 # this value allow imshow to initialise it's color scale
# axim3 = ax3.imshow(array)

# del array

# for _ in range(50):
#     print(".", end="")
#     matrix = np.random.randint(0, 100, size=(IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
    
#     axim1.set_data(matrix)
#     fig1.canvas.flush_events()
    
#     axim2.set_data(matrix)
#     fig1.canvas.flush_events()
    
#     axim3.set_data(matrix)
#     fig1.canvas.flush_events()