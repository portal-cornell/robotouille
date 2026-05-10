# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Robotouille

Robotouille is a benchmark environment for testing LLM agent planning capabilities. It simulates a kitchen where robots must complete long-horizon cooking tasks (synchronous, asynchronous, and multi-agent). The environment is built on Gym with PyGame rendering.

## Setup

```sh
python -m venv robotouille && source robotouille/bin/activate   # or conda/pyenv
pip install -e .
pip install -e agents/prompt_builder/gpt-cost-estimator
```

Set API keys (see `.envrctemplate`) before running LLM agents. The project uses [direnv](https://direnv.net/) via an `.envrc` file.

## Running

```sh
# Human play (default environment)
python main.py

# Specific environment
python main.py ++game.environment_name=high_level_lettuce_burger

# Procedurally generated (with seed)
python main.py ++game.environment_name=high_level_lettuce_burger ++game.seed=42

# Run an LLM agent experiment
python main.py +experiments=ReAct/synchronous/last-reasoning-action-mpc

# Override the LLM model
python main.py +experiments=IO/synchronous/io ++llm.llm_model=gemini-1.5-flash

# Collect human demonstration in-context examples
python main.py +experiments=human/custom_human ++game.environment_name=synchronous_train/0_cheese_onion_sandwich ++game.seed=26
```

## Testing

Backend unit tests (run from repository root):

```sh
python -m backend.tests.action_test
python -m backend.tests.pred_test
python -m backend.tests.delayed_sfx_test
python -m backend.tests.rep_sfx_test
```

Integration/environment tests (launches environments headlessly):

```sh
python backend/tests/test_envs.py          # base + composite environment tests
python backend/tests/test_procedural.py   # procedural generation tests
```

## Architecture

### Core execution flow

`main.py` → `robotouille/robotouille_simulator.py:run_robotouille()` → `robotouille/robotouille_env.py:create_robotouille_env()` → `robotouille/env.py:RobotouilleEnv`

The entry point uses **Hydra** for configuration (`conf/`). `main.py` either calls `play()` (single run) or `evaluate()` (batch evaluation across environments and seeds).

### Configuration system (Hydra)

`conf/config.yaml` composes three groups:
- `conf/game/base_game.yaml` — agent name, environment name, seed, max_steps, render mode, recording
- `conf/llm/base_llm.yaml` — LLM model, temperature, prompt version, in-context examples, logging
- `conf/evaluation/base_evaluation.yaml` — list of environments and seeds for batch evaluation

Experiment shortcuts live in `conf/experiments/` and override the base configs via `+experiments=<path>`.

### Backend (game engine)

`backend/` contains the PDDL-style planning engine decoupled from any rendering:

- `domain.py` — `Domain`: holds object types, predicate definitions, action definitions. `__deepcopy__` returns `self` (shared singleton).
- `predicate.py` — `Predicate`: typed, grounded fact. Used as dict keys (hashable).
- `action.py` — `Action`: preconditions + immediate effects + special effects.
- `state.py` — `State`: current grounded predicates, valid actions, goal check, and `step()`. `__deepcopy__` is optimised (domain/goal are shallow-copied; predicates/actions are dict-copied).
- `special_effect.py` + `special_effects/` — delayed, repetitive, conditional, creation, deletion effects triggered by actions.

### Environment loading

`environments/env_generator/builder.py` loads a JSON from `environments/env_generator/examples/` and builds a typed object list + predicate set. `environments/env_generator/procedural_generator.py` randomises object placement for a given seed.

`domain/robotouille.json` defines the full domain (object types, all predicate definitions, all action definitions). This is the authoritative source for what stations, items, and predicates exist.

### Agents

All agents inherit from `agents/agent.py:Agent` and must implement `propose_actions(obs, env)`. Register new agents in `agents/__init__.py:NAME_TO_AGENT`.

Available agents: `bfs`, `astar`, `human`, `io`, `io-cot`, `ReAct`, `Reflexion`.

LLM agents use `agents/prompt_builder/` for versioned prompt management (YAML templates in `agents/prompt_builder/prompts/`) and `agents/in_context_examples/` for few-shot examples stored under `agents/in_context_examples/data/`.

### Adding a new agent

1. Create a Python file in `agents/`.
2. Subclass `Agent` and implement `propose_actions`, `is_done`, and `is_retry`.
3. Add an entry to `NAME_TO_AGENT` in `agents/__init__.py`.

### Adding a new environment

Create a JSON in `environments/env_generator/examples/` following the format in `environments/env_generator/README.md`. Objects/stations must match the enums in `environments/env_generator/object_enums.py` and the predicates/actions in `domain/robotouille.json`.

## Key notes

- **PDDLGym support is currently broken** ([#37](https://github.com/portal-cornell/robotouille/issues/37)); use the native backend.
- `optimal_steps` in experiment configs are hardcoded per environment (BFS-based automatic calculation is tracked in [#38](https://github.com/portal-cornell/robotouille/issues/38)).
- `State.__deepcopy__` intentionally shares `domain` and `goal` references across copies for performance — do not mutate them on a copied state.
- Hydra outputs (logs, videos, results) go to `outputs/` by default.
