# Agents

This directory contains the code for agents used in Robotouille. These agents include:

- Human: A human agent that can interact with the environment using the keyboard and mouse
- LLM: Baselines including I/O, I/O CoT, and ReAct
- Classical: Baselines like BFS. (Currently too slow to be of any use [#38](https://github.com/portal-cornell/robotouille/issues/38))

## Prerequisites for running an LLM Agent

### Set your environment keys

To use API-based models you must set your environment keys. Check `.envrctemplate` for the required
keys. We use [direnv](https://direnv.net/) to load our environment variables using an `.envrc` file.

### Setup your agent
Check the Hydra `/conf/experiments` directory for the configuration files to run an LLM agent experiment. Specifically,
- the `llm` field allows for specifying the `llm_model`, the prompt to use from `prompt_builder` (see inner `README.md` for more information), and the `num_examples` along with the `example_dir_path` located under `in_context_examples`.
- the `game` field allows for specifying the `agent_name` corresponding to the strings in `__init__.py` and the `max_steps` for the agent to run for (or `max_step_multiplier` to multiply to the optimal number of steps for the environment).
- the `evaluation` field allows for specifying the `environment_names` to run on and the `testing_seeds` to run on each environment. Currently, the `optimal_steps` for each environment is hardcoded based on the default environment (seed=null) until [#38](https://github.com/portal-cornell/robotouille/issues/38) is resolved to calculate the optimal steps on the fly.

### Environments to choose
We provide environments to benchmark your LLM agents on, located under `environments/env_generator/examples/`. The benchmark environments are under the `synchronous/`, `asynchronous/`, and `multi_agent/` directories.

### Running an LLM Agent
To run an LLM agent, you can use the following command:
```sh
# Runs the ReAct agent on the entire synchronous dataset
python main.py +experiments=ReAct/synchronous/last-reasoning-action-mpc
```

## Usage Shortcuts

To replicate the experiments in the paper for gpt-4o, you can use the following commands:
```sh
# Runs the ReAct agent on the synchronous and asynchronous datasets
python main.py +experiments=ReAct/synchronous/last-reasoning-action-mpc
python main.py +experiments=ReAct/asynchronous/last-reasoning-action-mpc

# Runs the I/O agent on the entire synchronous and asynchronous datasets
python main.py +experiments=IO/synchronous/io
python main.py +experiments=IO/asynchronous/io

# Runs the I/O CoT agent on the entire synchronous and asynchronous datasets
python main.py +experiments=IO_CoT/synchronous/io-cot
python main.py +experiments=IO_CoT/asynchronous/io-cot
```

To run an agent on a different LLM model, you can override `llm.llm_model`
```sh
# Runs the I/O agent on the synchronous dataset with the gemini-1.5-flash model
python main.py +experiments=IO/synchronous/io ++llm.llm_model=gemini-1.5-flash
```

To collect human demonstrations formatted as ReAct in-context examples, you can use the following command:
```sh
# Collects human trajectories for the synchronous training set
python main.py +experiments=human/custom_human ++game.environment_name=synchronous_train/0_cheese_onion_sandwich ++game.seed=26
```
The in-context examples will be stored in the most recent Hydra `output` directory. The Reasoning will be left empty for a human to annotate.

Refer to the `conf/` directory for more information on values you can override. The `experiments` directory contains the configuration files for running agent experiments. The other directories contain base configurations with documented fields.