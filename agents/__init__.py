from .bfs_agent import BFSAgent
from .human import Human
from .IO_agent import IOAgent
from .IOCoT_agent import IOCoTAgent
from .ReAct_agent import ReActAgent
from .Reflexion_agent import ReflexionAgent
from .astar_pruning_agent import AStarPruningAgent
from .astar_agent import AStarAgent

# Modify this dictionary to register a custom agent
NAME_TO_AGENT = {
    "bfs": BFSAgent,
    "astar_pruning": AStarPruningAgent,
    "astar": AStarAgent,
    "human": Human,
    "io": IOAgent,
    "io-cot": IOCoTAgent,
    "ReAct": ReActAgent,
    "Reflexion": ReflexionAgent
}