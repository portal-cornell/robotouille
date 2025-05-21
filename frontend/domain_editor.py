import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIImage
from domain_elements import *
import json
import os
from pygame_gui.core import ObjectID

import tkinter as tk
from tkinter import filedialog


# tkinter to open native file dialog and return the selected file path
def open_file_dialog(title="Select a file", filetypes=None, initial_dir=None):
    root = tk.Tk()
    root.withdraw()  # hides the window

    if filetypes is None:
        filetypes = [("JSON files", "*.json"), ("All files", "*.*")]

    if initial_dir is None:
        initial_dir = os.path.expanduser("~")

    file_path = filedialog.askopenfilename(
        title=title, filetypes=filetypes, initialdir=initial_dir
    )

    root.destroy()
    return file_path


# open native SAVE file and return selected file path
def save_file_dialog(
    title="Save file", filetypes=None, initial_dir=None, default_extension=".json"
):

    root = tk.Tk()
    root.withdraw()

    if filetypes is None:
        filetypes = [("JSON files", "*.json"), ("All files", "*.*")]

    if initial_dir is None:
        initial_dir = os.path.expanduser("~")

    file_path = filedialog.asksaveasfilename(
        title=title,
        filetypes=filetypes,
        initialdir=initial_dir,
        defaultextension=default_extension,
    )

    root.destroy()
    return file_path


# loads json from file dialog or default file path
def load_json_data():
    global original_json_path

    file_path = open_file_dialog(
        title="Select Domain JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    if file_path:
        original_json_path = file_path
        with open(file_path, "r") as file:
            return json.load(file)
    return None


root = tk.Tk()
root.withdraw()
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

# global variable added
orginal_json_path = None
# predicate defs buttons in the left panel:
preds = []
pred_buttons = []

save_pred_buttons = {}  # dictionary for save predicate
# json initialization

data = load_json_data()
if data is None:
    # Fallback to default path
    json_path = os.path.join(
        os.path.dirname(__file__), "..", "domain", "robotouille.json"
    )
    json_path = os.path.normpath(json_path)
    original_json_path = json_path
    try:
        with open(json_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # Create empty structure if no file exists
        data = {"predicate_defs": [], "action_defs": []}


def find_slot(
    predicate_json, workspace: ActionWorkspace, section: str, container=center_panel
):

    for slot in workspace.slots:
        params = predicate_json.get("params", predicate_json.get("param"))
        if slot.occupied == None and slot.section == section:
            if section == "sfx":
                new_sfx = SFXWorkspace(
                    relative_rect=pygame.Rect(mouse_pos, (850, 700)),
                    manager=manager,
                    container=center_panel,
                    text=predicate_json["type"],
                )
                all_workspaces.append(new_sfx)
                if "conditions" in predicate_json:
                    for pred in predicate_json["conditions"]:
                        find_slot(pred, new_sfx, "preconditions", new_sfx)
                if "fx" in predicate_json:
                    for pred in predicate_json["fx"]:
                        find_slot(pred, new_sfx, "ifx", new_sfx)
                if "sfx" in predicate_json:
                    for pred in predicate_json["sfx"]:
                        find_slot(pred, new_sfx, "sfx", new_sfx)

                new_sfx.hide()
                block = DraggableBlock(
                    pygame.Rect((30, 30), (185, 40)),
                    manager=manager,
                    container=container,
                    text=predicate_json["type"],
                    param_defs=[],
                    sfx=True,
                    sfx_workspace=new_sfx,
                )
                slot.occupied = block
                block.docked_slot = slot
                workspace.attach_block(block, slot)
                break

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
            slot.occupied = block
            block.docked_slot = slot
            block.toggle_color()
            if predicate_json["is_true"]:
                block.toggle_color()
            else:
                block.toggle_color()
            workspace.attach_block(block, slot)
            # print(
            #     "Added "
            #     + predicate_json["predicate"]
            #     + " to slot at ("
            #     + str(slot.rel_pos[0])
            #     + ", "
            #     + str(slot.rel_pos[1])
            #     + "). It is in state: "
            #     + str(predicate_json["is_true"])
            # )
            break


def json_to_action(name: str, ws_x, ws_y, container=center_panel):
    # pull the action from the json
    action = None
    actions_json = data["action_defs"]
    # print(actions_json)
    for action_json in actions_json:
        # print(action_json["name"])
        if action_json["name"] == name:
            action = action_json

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

    for pred in action["sfx"]:
        find_slot(pred, loaded_act, "sfx")
    loaded_act.parametrize()
    return loaded_act


def populate_predicates():
    left_panel.get_container().clear()
    preds.clear()
    pred_buttons.clear()
    # get dimensions from image
    button_image_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", "buttons", "predicate.png"
    )
    if os.path.exists(button_image_path):
        button_image = pygame.image.load(button_image_path)
        button_width = button_image.get_width()
        button_height = button_image.get_height()
    else:
        button_width, button_height = 180, 40

    for pred in data["predicate_defs"]:
        preds.append(pred["name"])

    for i, text in enumerate(preds):
        button = UIButton(
            relative_rect=pygame.Rect(15, 10 + i * 50, button_width, button_height),
            text=text,
            manager=manager,
            container=left_panel,
            object_id="#new_predicate_button",
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

# create new action!
spawn_workspace_button = UIButton(
    relative_rect=pygame.Rect(460, 10, 110, 40),
    text="New Action",
    manager=manager,
    container=center_panel,
)

# create new object!
spawn_object_button = UIButton(
    relative_rect=pygame.Rect(570, 10, 110, 40),
    text="New Object",
    manager=manager,
    container=center_panel,
)

# buttons for loading/saving domain
load_domain_button = UIButton(
    relative_rect=pygame.Rect(680, 10, 110, 40),
    text="Load Domain",
    manager=manager,
    container=center_panel,
)

save_to_original_button = UIButton(
    relative_rect=pygame.Rect(790, 10, 110, 40),
    text="Save Domain",
    manager=manager,
    container=center_panel,
)

save_domain_button = UIButton(
    relative_rect=pygame.Rect(900, 10, 150, 40),
    text="Save New Domain",
    manager=manager,
    container=center_panel,
)


# little helper for calculating workspace coords
def calc_workspace_coords():
    temp_list = []
    for ws in all_workspaces:
        if not isinstance(ws, SFXWorkspace):
            temp_list.append(ws)
    if temp_list:
        last_ws = temp_list[-1]
        last_ws_rect = last_ws.get_relative_rect()
        ws_y = last_ws_rect.y + last_ws_rect.height + 25
    else:
        ws_y = 50
    ws_x = center_panel.rect.x - 50
    return ws_x, ws_y


def set_new_scrollable_dims():
    new_height = len(all_workspaces) * SCREEN_HEIGHT + 300
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
            elif event.ui_element in sfx_buttons:
                mouse_pos = pygame.mouse.get_pos()
                center_panel_topleft = center_panel.get_relative_rect().topleft
                relative_mouse_pos = (
                    mouse_pos[0] - center_panel_topleft[0],
                    mouse_pos[1] - center_panel_topleft[1],
                )
                new_sfx = SFXWorkspace(
                    relative_rect=pygame.Rect(mouse_pos, (850, 700)),
                    manager=manager,
                    container=center_panel,
                    text=event.ui_element.text,
                )
                all_workspaces.append(new_sfx)
                new_sfx.hide()
                new_sfx_block = DraggableBlock(
                    pygame.Rect((30, relative_mouse_pos[1]), (185, 40)),
                    manager=manager,
                    container=center_panel,
                    text=event.ui_element.text,
                    param_defs=[],
                    sfx=True,
                    sfx_workspace=new_sfx,
                )

            elif event.ui_element in action_buttons:
                ws_x, ws_y = calc_workspace_coords()
                new_action = json_to_action(event.ui_element.text, ws_x, ws_y)
                a_blocks = new_action.attached_blocks
                # print(a_blocks)
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
                    relative_rect=pygame.Rect(400, 0, 100, 50),
                    text="Save",
                    manager=manager,
                    container=pred_workspace,
                )
                save_pred_buttons[save_pred_button] = pred_workspace

                set_new_scrollable_dims()

            elif event.ui_element in save_pred_buttons:
                pred = save_pred_buttons[event.ui_element]
                pred_json = pred.serialize()
                print(pred_json)

                params = pred.parametrize()

                # case for empty
                if params:
                    param_defs = [("obj", (130, 15), params)]
                else:
                    param_defs = []
                new_block = DraggableBlock(
                    pygame.Rect(
                        pred.get_relative_rect().x,
                        pred.get_relative_rect().y,
                        185,
                        40,
                    ),
                    manager=manager,
                    container=center_panel,
                    text=pred.top_label.get_text(),
                    param_defs=param_defs,
                )

                pred.kill()
                blocks.append(new_block)

            elif event.ui_element == load_domain_button:
                new_data = load_json_data()
                if new_data:
                    data = new_data

                    if left_panel.showing_predicates:
                        populate_predicates()
                    else:
                        populate_actions()
                    # kill existing workspaces
                    for ws in all_workspaces[:]:
                        ws.kill()
                    all_workspaces.clear()

            elif event.ui_element == save_domain_button:
                file_path = save_file_dialog(
                    title="Save Domain File",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                )

                if file_path:
                    # save_data = {
                    #     "predicate_defs": data.get("predicate_defs", []),
                    #     "action_defs": [],
                    # }
                    save_data = {
                        "version": data.get("version", "1.0.0"),
                        "name": data.get("name", "robotouille"),
                        "input_json": data.get("input_json", "domain/input.json"),
                        "object_types": data.get(
                            "object_types",
                            ["station", "item", "player", "container", "meal"],
                        ),
                        "predicate_defs": data.get("predicate_defs", []),
                        "action_defs": data.get("action_defs", []),
                        "objects": data.get("objects", []),
                    }
                    # i create a dictionary of preexisting items for the code to do a lookup
                    existing_actions = {
                        action["name"]: i
                        for i, action in enumerate(save_data["action_defs"])
                    }
                    existing_predicates = {
                        pred["name"]: i
                        for i, pred in enumerate(save_data["predicate_defs"])
                    }
                    existing_objects = {
                        obj["name"]: i
                        for i, obj in enumerate(save_data.get("objects", []))
                    }

                    # need to add all workspace actions
                    for ws in all_workspaces:
                        if isinstance(ws, ActionWorkspace):
                            action_data = ws.serialize()
                            action_name = action_data["name"]

                            # updat action if it already eixts othr wise add action
                            if action_name in existing_actions:
                                save_data["action_defs"][
                                    existing_actions[action_name]
                                ] = action_data
                            else:
                                save_data["action_defs"].append(action_data)

                        elif isinstance(ws, PredicateCreator):

                            pred_data = ws.serialize()
                            pred_name = pred_data["name"]
                            # same thing
                            if pred_name in existing_predicates:
                                save_data["predicate_defs"][
                                    existing_predicates[pred_name]
                                ] = pred_data
                            else:
                                save_data["predicate_defs"].append(pred_data)

                        elif isinstance(ws, ObjectWorkspace):
                            obj_data = ws.serialize()
                            obj_name = obj_data["name"]

                            # updat ethe object if it alreayd exists othewirse add the object
                            if obj_name in existing_objects:
                                save_data["objects"][
                                    existing_objects[obj_name]
                                ] = obj_data
                            else:
                                if "objects" not in save_data:
                                    save_data["objects"] = []
                                save_data["objects"].append(obj_data)
                    with open(file_path, "w") as f:
                        json.dump(save_data, f, indent=4)

                    print(f"Domain saved to: {file_path}")
            elif event.ui_element == save_to_original_button:
                if original_json_path:
                    # this is just the same logic for saving domain/predicate/action as a new .json file that i did, except this saves to the original robotoullie.json
                    # TODO: i like the option to save your changes to a new .json, but might remove if unncesseary
                    save_data = {
                        "version": data.get("version", "1.0.0"),
                        "name": data.get("name", "robotouille"),
                        "input_json": data.get("input_json", "domain/input.json"),
                        "object_types": data.get(
                            "object_types",
                            ["station", "item", "player", "container", "meal"],
                        ),
                        "predicate_defs": data.get("predicate_defs", []),
                        "action_defs": data.get("action_defs", []),
                        "objects": data.get("objects", []),
                    }

                    existing_actions = {
                        action["name"]: i
                        for i, action in enumerate(save_data["action_defs"])
                    }
                    existing_predicates = {
                        pred["name"]: i
                        for i, pred in enumerate(save_data["predicate_defs"])
                    }
                    existing_objects = {
                        obj["name"]: i
                        for i, obj in enumerate(save_data.get("objects", []))
                    }

                    for ws in all_workspaces:
                        if isinstance(ws, ActionWorkspace):
                            action_data = ws.serialize()
                            action_name = action_data["name"]

                            if action_name in existing_actions:
                                save_data["action_defs"][
                                    existing_actions[action_name]
                                ] = action_data
                            else:
                                save_data["action_defs"].append(action_data)

                        elif isinstance(ws, PredicateCreator):
                            pred_data = ws.serialize()
                            pred_name = pred_data["name"]

                            if pred_name in existing_predicates:
                                save_data["predicate_defs"][
                                    existing_predicates[pred_name]
                                ] = pred_data
                            else:
                                save_data["predicate_defs"].append(pred_data)

                        elif isinstance(ws, ObjectWorkspace):
                            obj_data = ws.serialize()
                            obj_name = obj_data["name"]

                            if obj_name in existing_objects:
                                save_data["objects"][
                                    existing_objects[obj_name]
                                ] = obj_data
                            else:
                                if "objects" not in save_data:
                                    save_data["objects"] = []
                                save_data["objects"].append(obj_data)

                    # save directly to the roboutille.json
                    with open(original_json_path, "w") as f:
                        json.dump(save_data, f, indent=4)

                    print(f"Domain saved to original file: {original_json_path}")
                else:
                    print("No original file loaded. Please load a file first.")

        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element in action_buttons:
                mouse_pos = pygame.mouse.get_pos()
                action = json_to_action(
                    event.ui_element.text, mouse_pos[0], mouse_pos[1], container=None
                )
                temp_workspaces.append(action)
                action.preview_layer(5)
            elif event.ui_element in sfx_buttons:
                mouse_pos = pygame.mouse.get_pos()
                sfx = SFXWorkspace(
                    relative_rect=pygame.Rect(mouse_pos, (850, 700)),
                    manager=manager,
                    container=None,
                    text=event.ui_element.text,
                )
                temp_workspaces.append(sfx)
                sfx.preview_layer(5)

        if event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            if event.ui_element in action_buttons or event.ui_element in sfx_buttons:
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
    window_surface.fill(pygame.Color("#61ACF8"))
    manager.draw_ui(window_surface)
    for ws in all_workspaces:
        if isinstance(ws, ActionWorkspace):
            ws.draw_debug_slots(window_surface)
        if isinstance(ws, SFXWorkspace):
            if not ws.hidden:
                ws.draw_debug_slots(window_surface)

    pygame.display.update()

pygame.quit()
