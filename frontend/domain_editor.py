import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from domain_elements import *

pygame.init()
pygame.display.set_caption("Domain Editor")

# Window & manager
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
window_surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
)
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))


# Panels
LEFT_WIDTH = 200
RIGHT_WIDTH = 200
CENTER_WIDTH = SCREEN_WIDTH - LEFT_WIDTH - RIGHT_WIDTH

INITIAL_TOTAL = 1600
INITIAL_SIDE = 200
SIDE_RATIO = INITIAL_SIDE / INITIAL_TOTAL

left_panel = EditorPanel(
    pygame.Rect(0, 0, LEFT_WIDTH, SCREEN_HEIGHT),
    manager,
    starting_height=1,
    bg_color=pygame.Color("#DCEAF4"),
)
center_panel = EditorPanel(
    pygame.Rect(LEFT_WIDTH, 0, CENTER_WIDTH, SCREEN_HEIGHT), manager
)
right_panel = EditorPanel(
    pygame.Rect(SCREEN_WIDTH - RIGHT_WIDTH, 0, RIGHT_WIDTH, SCREEN_HEIGHT),
    manager,
    starting_height=1,
    bg_color=pygame.Color("#DCEAF4"),
)

left_panel.set_anchors({"top": "top", "bottom": "bottom", "left": "left"})
left_panel.get_container().set_anchors(
    {"top": "top", "bottom": "bottom", "left": "left"}
)

center_panel.set_anchors(
    {"top": "top", "bottom": "bottom", "left": "left", "right": "right"}
)
center_panel.get_container().set_anchors(
    {"top": "top", "bottom": "bottom", "left": "left", "right": "right"}
)

right_panel.set_anchors({"top": "top", "bottom": "bottom", "right": "right"})
right_panel.get_container().set_anchors(
    {"top": "top", "bottom": "bottom", "right": "right"}
)

left_panel.set_scrollable_area_dimensions((LEFT_WIDTH, SCREEN_HEIGHT * 2))
center_panel.set_scrollable_area_dimensions((CENTER_WIDTH, SCREEN_HEIGHT * 2))
right_panel.set_scrollable_area_dimensions((RIGHT_WIDTH, SCREEN_HEIGHT * 2))


# "preset" buttons in the left panel:
preset_texts = ["iscuttable", "isfried", "iscooked", "isboard", "loc", "isrolled"]
preset_buttons = []
for i, text in enumerate(preset_texts):
    button = UIButton(
        relative_rect=pygame.Rect(10, 10 + i * 50, 180, 40),
        text=text,
        manager=manager,
        container=left_panel,
    )
    preset_buttons.append(button)

# create new action!
spawn_workspace_button = UIButton(
    relative_rect=pygame.Rect(10, 10 + len(preset_texts) * 50, 180, 40),
    text="New Action",
    manager=manager,
    container=left_panel,
)

# preset predicate parameters:
# i1 = UIButton(
#     relative_rect=pygame.Rect(60, 60 + len(preset_texts) * 50, 30, 30),
#     text="i1",
#     manager=manager,
#     container=left_panel,
# )

# preset_buttons.append(i1)


clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:

            if event.ui_element in preset_buttons:

                mouse_pos = pygame.mouse.get_pos()
                center_panel_topleft = center_panel.get_relative_rect().topleft
                relative_mouse_pos = (
                    mouse_pos[0] - center_panel_topleft[0],
                    mouse_pos[1] - center_panel_topleft[1],
                )

                # if event.ui_element == i1:
                #     new_block = DraggableBlock(
                #         relative_rect=pygame.Rect(
                #             (30, relative_mouse_pos[1]), (30, 30)
                #         ),
                #         manager=manager,
                #         container=center_panel,
                #         text=event.ui_element.text,
                #         starting_height=3,
                #         is_parameter=True,
                #     )

                new_block = DraggableBlock(
                    pygame.Rect((30, relative_mouse_pos[1]), (120, 40)),
                    manager=manager,
                    container=center_panel,
                    text=event.ui_element.text,
                    param_defs=[
                        ("obj", (130, 15), ["i1", "s1"]),
                    ],
                )

                blocks.append(new_block)
            elif event.ui_element == spawn_workspace_button:
                ws_x = center_panel.rect.x
                ws_y = center_panel.rect.y + 50
                new_ws = ActionWorkspace(
                    relative_rect=pygame.Rect(ws_x - 50, ws_y, 700, 700),
                    manager=manager,
                    container=center_panel,
                )
                all_workspaces.append(new_ws)

        if event.type == pygame.VIDEORESIZE:

            new_w, new_h = event.w, event.h
            new_side = int(new_w * SIDE_RATIO)
            new_center = new_w - 2 * new_side

            window_surface = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
            manager.set_window_resolution((new_w, new_h))

            left_panel.set_dimensions((new_side, new_h))
            center_panel.set_dimensions((new_center, new_h))
            right_panel.set_dimensions((new_side, new_h))

            left_panel.set_relative_position((0, 0))
            center_panel.set_relative_position((new_side, 0))
            right_panel.set_relative_position((new_side + new_center, 0))

            left_panel.set_scrollable_area_dimensions((new_side, new_h * 2))
            center_panel.set_scrollable_area_dimensions((new_center, new_h * 2))
            right_panel.set_scrollable_area_dimensions((new_side, new_h * 2))

    manager.update(time_delta)
    window_surface.fill(pygame.Color("#EDE8D0"))
    manager.draw_ui(window_surface)
    for ws in all_workspaces:
        ws.draw_debug_slots(window_surface)
    pygame.display.update()

pygame.quit()
