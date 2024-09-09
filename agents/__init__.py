from .bfs_agent import BFSAgent
from .human import Human
from .IO_agent import IOAgent
from .ReAct_agent import ReActAgent

# Modify this dictionary to register a custom agent
NAME_TO_AGENT = {
    "bfs": BFSAgent,
    "human": Human,
    "io": IOAgent,
    "ReAct": ReActAgent,
}