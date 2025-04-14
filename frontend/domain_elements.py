import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextBox


# def update_positions(root):
#     stack = [root]
#     while stack:
#         current = stack.pop()

#         for child in current.child_blocks:

#             child.abs_pos = current.abs_pos + child.local_offset
#             child.set_relative_position(child.abs_pos)
#             stack.append(child)


class DraggableBlock(UIButton):
    def __init__(self, relative_rect, manager, text="", container=None, **kwargs):
        # The 'starting_height' or 'starting_layer_height' param ensures it’s above panels
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            text=text,
            starting_height=2,
            **kwargs,
        )
        self.is_dragging = False
        self.drag_offset = (0, 0)
        self.mouse_down_pos = None
        self.toggled = False

    def toggle_color(self):
        self.toggled = not self.toggled
        if self.toggled:
            self.colours["normal_bg"] = pygame.Color("green")
            self.colours["hovered_bg"] = pygame.Color("darkgreen")
        else:
            self.colours["normal_bg"] = pygame.Color("red")
            self.colours["hovered_bg"] = pygame.Color("darkred")
        self.rebuild()

    def process_event(self, event):
        handled = super().process_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self.mouse_down_pos = event.pos
                abs_rect = self.get_abs_rect()
                mouse_x, mouse_y = event.pos
                self.drag_offset = (abs_rect.x - mouse_x, abs_rect.y - mouse_y)
                return handled

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                self.unfocus()

                # Check if mouse moved significantly -> drag vs click
                if self.mouse_down_pos is not None:
                    dx = abs(event.pos[0] - self.mouse_down_pos[0])
                    dy = abs(event.pos[1] - self.mouse_down_pos[1])
                    if dx < 5 and dy < 5:  # Treat as a click
                        self.toggle_color()

                return handled

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x, mouse_y = event.pos

            abs_new_x = mouse_x + self.drag_offset[0]
            abs_new_y = mouse_y + self.drag_offset[1]

            container_rect = (
                self.ui_container.get_abs_rect()
                if self.ui_container
                else pygame.Rect(0, 0, 0, 0)
            )

            rel_new_x = abs_new_x - container_rect.x
            rel_new_y = abs_new_y - container_rect.y

            self.set_relative_position((rel_new_x, rel_new_y))

        return handled


class EditorPanel(UIPanel):
    def __init__(self, relative_rect, manager, bg_color=pygame.Color("#2d2d2d")):
        super().__init__(relative_rect=relative_rect, manager=manager)
        self.background_colour = bg_color
        self.rebuild()


class ActionWorkspace(UIPanel):
    def __init__(
        self,
        relative_rect,
        manager,
        container=None,
        text="New Action",
        bg_color=pygame.Color(168, 208, 230),
        **kwargs
    ):
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            starting_height=1,
            **kwargs,
        )
        self.background_colour = bg_color
        self.rebuild()
        self.attached_blocks = []
        self.top_label = UITextBox(
            html_text="<font color=#FFFFFF><b>New Action</b></font>",
            relative_rect=pygame.Rect(0, 0, 500, 50),
            manager=manager,
            container=self,
        )

        self.preconditions_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Preconditions</b></font>",
            relative_rect=pygame.Rect(0, 50, 150, 50),
            manager=manager,
            container=self,
        )

        self.immediateFX_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Immediate FX</b></font>",
            relative_rect=pygame.Rect(0, 250, 150, 50),
            manager=manager,
            container=self,
        )

        self.specialFX_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Special FX</b></font>",
            relative_rect=pygame.Rect(0, 400, 150, 50),
            manager=manager,
            container=self,
        )

    def attach_block(self, block):
        self.attached_blocks.append(block)
