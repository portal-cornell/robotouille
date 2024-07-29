from .human import Human
from .ReAct_agent import ReActAgent

# Modify this dictionary to register a custom agent
NAME_TO_AGENT = {
    "human": Human,
    "ReAct": ReActAgent,
}