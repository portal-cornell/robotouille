import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIImage
from domain_elements import *
import json
import os
from pygame_gui.core import ObjectID


pygame.init()
pygame.display.set_caption("Domain Editor")


# window & manager
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000
window_surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
)
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), "theme.json")


# panels
LEFT_WIDTH = 250
RIGHT_WIDTH = 250
CENTER_WIDTH = SCREEN_WIDTH - LEFT_WIDTH - RIGHT_WIDTH

INITIAL_TOTAL = 1600
INITIAL_SIDE = 250
SIDE_RATIO = INITIAL_SIDE / INITIAL_TOTAL

left_panel = EditorPanel(
    pygame.Rect(0, 0, LEFT_WIDTH, SCREEN_HEIGHT),
    manager,
    starting_height=1,
    bg_color=pygame.Color("#DCEAF4"),
    allow_scroll_x=False,
)
center_panel = EditorPanel(
    pygame.Rect(LEFT_WIDTH, 0, CENTER_WIDTH, SCREEN_HEIGHT), manager
)
right_panel = EditorPanel(
    pygame.Rect(SCREEN_WIDTH - RIGHT_WIDTH, 0, RIGHT_WIDTH, SCREEN_HEIGHT),
    manager,
    starting_height=1,
    bg_color=pygame.Color("#DCEAF4"),
    allow_scroll_x=False,
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

left_panel.set_scrollable_area_dimensions((LEFT_WIDTH, SCREEN_HEIGHT * 3))
center_panel.set_scrollable_area_dimensions((CENTER_WIDTH, SCREEN_HEIGHT * 2))
right_panel.set_scrollable_area_dimensions((RIGHT_WIDTH, SCREEN_HEIGHT * 2))


# predicate defs buttons in the left panel:
preds = []
pred_buttons = []

# json initialization

json_path = os.path.join(os.path.dirname(__file__), "..", "domain", "robotouille.json")
json_path = os.path.normpath(json_path)
with open(json_path, "r") as file:
    data = json.load(file)


def find_slot(
    predicate_json, workspace: ActionWorkspace, section: str, container=center_panel
):
    for slot in workspace.slots:
        params = predicate_json.get("params", predicate_json.get("param"))
        if slot.occupied == None and slot.section == section:
            block = DraggableBlock(
                pygame.Rect((30, 30), (185, 40)),
                manager=manager,
                container=container,
                text=predicate_json["predicate"],
                param_defs=[
                    ("obj", (130, 15), params),
                ],
                is_true=predicate_json["is_true"],
                starting_height=workspace.get_starting_height(),
            )
            block.toggle_color()
            if predicate_json["is_true"]:
                block.toggle_color()
            else:
                block.toggle_color()
            workspace.attach_block(block, slot)
            print(
                "Added "
                + predicate_json["predicate"]
                + " to slot at ("
                + str(slot.rel_pos[0])
                + ", "
                + str(slot.rel_pos[1])
                + "). It is in state: "
                + str(predicate_json["is_true"])
            )
            break


def json_to_action(name: str, ws_x, ws_y, container=center_panel):
    # pull the action from the json
    action = None
    actions_json = data["action_defs"]
    print(actions_json)
    for action_json in actions_json:
        print(action_json["name"])
        if action_json["name"] == name:
            action = action_json

    print(action)

    # create a new action workspace
    loaded_act = ActionWorkspace(
        relative_rect=pygame.Rect(ws_x - 100, ws_y, 850, 700),
        manager=manager,
        container=container,
        text=action["name"],
        starting_height=1,
    )

    for pred in action["precons"]:
        find_slot(pred, loaded_act, "preconditions", container)

    for pred in action["immediate_fx"]:
        find_slot(pred, loaded_act, "ifx", container)

    # for pred in action["sfx"]:
    #     find_slot(pred, loaded_act, "sfx")
    loaded_act.parametrize()
    return loaded_act


def populate_predicates():
    left_panel.get_container().clear()

    preds.clear()
    pred_buttons.clear()

    for pred in data["predicate_defs"]:
        preds.append(pred["name"])

    for i, text in enumerate(preds):
        button = UIButton(
            relative_rect=pygame.Rect(10, 10 + i * 50, 180, 40),
            text=text,
            manager=manager,
            container=left_panel,
        )
        pred_buttons.append(button)


# action defs buttons in left panel
actions = []
action_buttons = []
action_hover = None


# helper func to determine an action's parameters
def identify_params(name: str):
    params = {}
    actions = data["action_defs"]
    action = actions[name]
    for precon in action["precons"]:
        for param in precon["params"]:
            params.add(param)
    for ifx in action["immediate_fx"]:
        for param in ifx["params"]:
            params.add(param)


def populate_actions():
    left_panel.get_container().clear()

    actions.clear()
    action_buttons.clear()
    for action in data["action_defs"]:
        actions.append(action["name"])

    for i, text in enumerate(actions):
        button = UIButton(
            relative_rect=pygame.Rect(10, 10 + i * 50, 180, 40),
            text=text,
            manager=manager,
            container=left_panel,
        )
        action_buttons.append(button)


# TODO fix all this, doesn't work right now
# current_dir = os.path.dirname(__file__)
# assets_dir = os.path.normpath(os.path.join(current_dir, "..", "assets"))

# ignore_list = {".DS_Store", "tileset", "frontend"}

# asset_buttons = []
# asset_paths = []

# for filename in os.listdir(assets_dir):

#     if filename in ignore_list:
#         continue

#     full_path = os.path.join(assets_dir, filename)

#     if os.path.isfile(full_path) and filename.lower().endswith(".png"):
#         asset_paths.append(full_path)


# def populate_assets():
#     right_panel.get_container().clear()

#     for i, name in enumerate(asset_paths):

#         image_surface = pygame.image.load(name).convert_alpha()
#         button = UIImage(
#             relative_rect=pygame.Rect(0, 10 + i * 50, 50, 50),
#             image_surface=image_surface,
#             manager=manager,
#             container=right_panel,
#         )
#         button.set_image(image_surface)
#         asset_buttons.append(button)


# populate_assets()

sfxs = ["conditional", "repetitive", "delayed"]
sfx_buttons = []


def populate_sfx():
    left_panel.get_container().clear()
    sfx_buttons.clear()
    for i, text in enumerate(sfxs):
        button = UIButton(
            relative_rect=pygame.Rect(10, 10 + i * 50, 180, 40),
            text=text,
            manager=manager,
            container=left_panel,
        )
        button.colours["normal_bg"] = pygame.Color(30, 0, 93)
        button.rebuild()
        sfx_buttons.append(button)


populate_predicates()


# create new action!
spawn_workspace_button = UIButton(
    relative_rect=pygame.Rect(680, 10, 110, 40),
    text="New Action",
    manager=manager,
    container=center_panel,
)

# create new object!
spawn_object_button = UIButton(
    relative_rect=pygame.Rect(790, 10, 110, 40),
    text="New Object",
    manager=manager,
    container=center_panel,
)


# buttons for toggling predicates to
toggle_button = UIButton(
    relative_rect=pygame.Rect(10, 10, 150, 40),
    text="Show Actions",
    manager=manager,
    container=center_panel,
)

show_sfx_button = UIButton(
    relative_rect=pygame.Rect(160, 10, 150, 40),
    text="Show SFX",
    manager=manager,
    container=center_panel,
)

new_pred_button = UIButton(
    relative_rect=pygame.Rect(310, 10, 150, 40),
    text="New Predicate",
    manager=manager,
    container=center_panel,
)

pred_buttons = {}


# little helper for calculating workspace coords
def calc_workspace_coords():
    if all_workspaces:
        last_ws = all_workspaces[-1]
        last_ws_rect = last_ws.get_relative_rect()
        ws_y = last_ws_rect.y + last_ws_rect.height + 25
    else:
        ws_y = 50
    ws_x = center_panel.rect.x - 50
    return ws_x, ws_y


def set_new_scrollable_dims():
    new_height = len(all_workspaces) * SCREEN_HEIGHT + 100
    new_width = center_panel.scrollable_container.relative_rect.width
    center_panel.set_scrollable_area_dimensions((new_width, new_height))


clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:

            if event.ui_element in pred_buttons:

                mouse_pos = pygame.mouse.get_pos()
                center_panel_topleft = center_panel.get_relative_rect().topleft
                relative_mouse_pos = (
                    mouse_pos[0] - center_panel_topleft[0],
                    mouse_pos[1] - center_panel_topleft[1],
                )

                params = data["predicate_defs"]
                param_list = []
                i, s, p, c, m = 1, 1, 1, 1, 1
                for param in params:
                    if param["name"] == event.ui_element.text:
                        for param_type in param["param_types"]:
                            if param_type[0] == "i":
                                param_list.append("i" + str(i))
                                i += 1
                            elif param_type[0] == "s":
                                param_list.append("s" + str(s))
                                s += 1
                            elif param_type[0] == "p":
                                param_list.append("p" + str(p))
                                p += 1
                            elif param_type[0] == "c":
                                param_list.append("c" + str(c))
                                c += 1
                            else:
                                param_list.append("m" + str(m))
                                m += 1

                new_block = DraggableBlock(
                    pygame.Rect((30, relative_mouse_pos[1]), (185, 40)),
                    manager=manager,
                    container=center_panel,
                    text=event.ui_element.text,
                    param_defs=[
                        ("obj", (130, 15), param_list),
                    ],
                )

                blocks.append(new_block)
            elif event.ui_element in action_buttons:
                ws_x, ws_y = calc_workspace_coords()
                new_action = json_to_action(event.ui_element.text, ws_x, ws_y)
                a_blocks = new_action.attached_blocks
                print(a_blocks)
                all_workspaces.append(new_action)
                set_new_scrollable_dims()
            elif event.ui_element == spawn_workspace_button:

                ws_x, ws_y = calc_workspace_coords()

                new_ws = ActionWorkspace(
                    relative_rect=pygame.Rect(ws_x - 100, ws_y, 850, 700),
                    manager=manager,
                    container=center_panel,
                )
                all_workspaces.append(new_ws)
                set_new_scrollable_dims()
            elif event.ui_element == spawn_object_button:
                ws_x, ws_y = calc_workspace_coords()
                new_ws = ObjectWorkspace(
                    relative_rect=pygame.Rect(ws_x - 100, ws_y, 700, 800),
                    manager=manager,
                    container=center_panel,
                )
                all_workspaces.append(new_ws)
                set_new_scrollable_dims()
            elif event.ui_element == toggle_button:
                left_panel.showing_predicates = not left_panel.showing_predicates

                if left_panel.showing_predicates:
                    toggle_button.set_text("Show Actions")
                    populate_predicates()
                else:
                    toggle_button.set_text("Show Predicates")
                    populate_actions()
            elif event.ui_element == show_sfx_button:
                populate_sfx()
            elif event.ui_element == new_pred_button:
                ws_x, ws_y = calc_workspace_coords()
                rel_rect = pygame.Rect(ws_x - 100, ws_y, 500, 100)
                pred_workspace = PredicateCreator(
                    relative_rect=rel_rect,
                    manager=manager,
                    container=center_panel,
                )
                all_workspaces.append(pred_workspace)
                save_pred_button = UIButton(
                    relative_rect=pygame.Rect(
                        rel_rect.x + 300, rel_rect.y - 50, 100, 50
                    ),
                    text="Save",
                    manager=manager,
                    container=pred_workspace.get_container(),
                )
                pred_buttons[save_pred_button] = pred_workspace

                set_new_scrollable_dims()
            elif event.ui_element in pred_buttons:
                pred = pred_buttons[event.ui_element]
                pred_json = pred.serialize()

        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element in action_buttons:
                mouse_pos = pygame.mouse.get_pos()
                action = json_to_action(
                    event.ui_element.text, mouse_pos[0], mouse_pos[1], container=None
                )
                temp_workspaces.append(action)
                action.preview_layer(5)

        if event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            if event.ui_element in action_buttons:
                for w in temp_workspaces:
                    w.kill()
                temp_workspaces.clear()

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
        if isinstance(ws, ActionWorkspace):
            ws.draw_debug_slots(window_surface)
    pygame.display.update()

pygame.quit()
