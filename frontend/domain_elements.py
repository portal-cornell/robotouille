import pygame
import pygame_gui
from pygame_gui.elements import *


class DraggableBlock(UIButton):
    def __init__(self, relative_rect, manager, text="", parent_block=None, **kwargs):
        super().__init__(relative_rect, manager, text=text, **kwargs)
        self.parent_block = parent_block
        self.child_blocks = []
        self.local_offset = (0, 0)
        self.is_dragging = False
        self.toggle_state = False

    def toggle(self):
        self.toggle_state = not self.toggle_state


class EditorPanel(UIPanel):
    def __init__(self, relative_rect, manager, **kwargs):
        super().__init__(relative_rect, manager, **kwargs)
        self.blocks = []

    def add_block(self, block):
        # TODO
        return

    def serialize(self):
        return [b.serialize() for b in self.blocks]


# handling block dragging:


def get_global_position(block):
    if block.parent:
        return get_global_position(block.parent) + block.local_offset
    else:
        return block.local_offset


# 4/12 trying a stack now becausse last time the recursion depth was hit when i did it
# recursively:


def update_positions(root):
    stack = [root]

    while stack:
        current = stack.pop()

        for child in current.children:
            child.abs_pos = current.abs_pos + child.local_offset
            stack.append(child)
