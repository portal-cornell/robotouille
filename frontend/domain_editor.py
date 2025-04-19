import pygame
import pygame_gui
from pygame_gui.elements import UIButton
from domain_elements import *

pygame.init()
pygame.display.set_caption("Domain Editor")

# Window & manager
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
window_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Panels
LEFT_WIDTH = 200
RIGHT_WIDTH = 200
CENTER_WIDTH = SCREEN_WIDTH - LEFT_WIDTH - RIGHT_WIDTH

left_panel = EditorPanel(pygame.Rect(0, 0, LEFT_WIDTH, SCREEN_HEIGHT), manager)
center_panel = EditorPanel(
    pygame.Rect(LEFT_WIDTH, 0, CENTER_WIDTH, SCREEN_HEIGHT), manager
)
right_panel = EditorPanel(
    pygame.Rect(SCREEN_WIDTH - RIGHT_WIDTH, 0, RIGHT_WIDTH, SCREEN_HEIGHT), manager
)

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
                    pygame.Rect((30, relative_mouse_pos[1]), (200, 60)),
                    manager=manager,
                    container=center_panel,
                    text="iscuttable",
                    param_defs=[
                        ("obj", (130, 15), ["i1", "s1"]),
                    ],
                )

                blocks.append(new_block)
            elif event.ui_element == spawn_workspace_button:
                ws_x = center_panel.rect.x + 50
                ws_y = center_panel.rect.y + 50
                new_ws = ActionWorkspace(
                    relative_rect=pygame.Rect(ws_x, ws_y, 700, 700),
                    manager=manager,
                    # no container => root UI container;
                )
                all_workspaces.append(new_ws)

    manager.update(time_delta)
    window_surface.fill(pygame.Color("#EDE8D0"))
    manager.draw_ui(window_surface)
    # for ws in all_workspaces:
    #     ws.draw_debug_slots(window_surface)
    pygame.display.update()

pygame.quit()
