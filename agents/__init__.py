from .bfs_agent import BFSAgent
from .human import Human
from .ReAct_agent import ReActAgent

# Modify this dictionary to register a custom agent
NAME_TO_AGENT = {
    "bfs": BFSAgent,
    "human": Human,
    "ReAct": ReActAgent,
}