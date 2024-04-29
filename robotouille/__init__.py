from rl.marl.marl_wrapper import MARLWrapper
from rl.marl.multiagent_hospital_env import MAHospital_robotouille
from robotouille.robotouille_env import RobotouilleRenderer, create_robotouille_env
from robotouille.robotouille_simulator import simulator

config = {
    "num_cuts": {"lettuce": 3, "default": 3},
    "cook_time": {"patty": 3, "default": 3},
}

env, json, renderer = create_robotouille_env("multiagent", 42, False)
obs, info = env.reset()

ENVIRONMENT = MAHospital_robotouille(env, config, renderer)
