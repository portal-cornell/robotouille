import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel,
    UIButton,
    UIScrollingContainer,
    UITextBox,
    UIDropDownMenu,
    UITextEntryBox,
    UIImage,
)
from pygame_gui.windows import UIFileDialog
from pygame_gui.core import ObjectID
import os
import json

import tkinter as tk
from tkinter import filedialog

# other json initialization

# json_path = os.path.join(os.path.dirname(__file__), "..", "domain", "robotouille.json")
# json_path = os.path.normpath(json_path)

# out_file = open(json_path, "w")


def open_file_dialog(title="Select a file", filetypes=None, initial_dir=None):
    """Opens a native file dialog and returns the selected file path"""
    root = tk.Tk()
    root.withdraw()

    if filetypes is None:
        filetypes = [("All files", "*.*")]

    if initial_dir is None:
        initial_dir = os.path.expanduser("~")

    file_path = filedialog.askopenfilename(
        title=title, filetypes=filetypes, initialdir=initial_dir
    )

    root.destroy()
    return file_path


SNAP_TOLERANCE = 20
all_workspaces = []
temp_workspaces = []
blocks = []

current_id = 0

blocks_by_id = {}
block_slots = {}

# button color constants
PLAYER_C = "633B48"
ITEM_C = "21005D"
STATION_C = "852221"
MEAL_C = "BF6A02"


class Slot:
    """A docking slot living inside an ActionWorkspace."""

    def __init__(self, rel_pos, section=None):
        self.rel_pos = rel_pos  # tuple (x,y) inside the workspace
        self.size = (185, 40)  # same size as block
        self.occupied = None  # points to DraggableBlock or None
        self.section = section
        self.hidden = False
        self.workspace = None

    def rect(self):
        return pygame.Rect(self.rel_pos, self.size)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    # for debugging
    def show_section(self):
        print(self.section)


class PredicateSlot:
    """A slot specifically for predicate blocks in asset configurations"""
    
    def __init__(self, rel_pos, asset_slot):
        self.rel_pos = rel_pos  # tuple (x,y) relative to asset config container
        self.size = (120, 25)  # smaller than regular slots
        self.occupied = None  # points to DraggableBlock or None
        self.asset_slot = asset_slot  # reference to parent AssetConfigSlot
        self.hidden = False

    def rect(self):
        return pygame.Rect(self.rel_pos, self.size)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False


class DraggableBlock(UIButton):
    def __init__(
        self,
        relative_rect,
        manager,
        text,
        container,
        param_defs=None,
        is_true=False,
        starting_height=2,
        sfx=False,
        sfx_workspace=None,
        **kwargs,
    ):

        # the block *itself* (acts as the drag handle too)
        super().__init__(
            relative_rect=relative_rect,
            text=text,
            manager=manager,
            container=container,
            starting_height=starting_height,
            **kwargs,
        )
        # Store param definitions but don't create dropdowns
        self._param_widgets = []  # list of (offset, widget) - kept empty now
        self.params = param_defs
        # drag state
        self.is_dragging = False
        self._drag_offset = (0, 0)
        self.docked_slot = None
        self.toggled = is_true

        # for special fx case
        self.is_sfx = sfx
        self.sfx_workspace = sfx_workspace
        if sfx:
            self.colours["normal_bg"] = pygame.Color(30, 0, 93)
            self.rebuild()

        self.base_container = container

        self.slot_section = None
        global current_id
        self.id = current_id
        current_id += 1
        blocks_by_id[self.id] = self

    def to_json(self):
        if self.is_sfx:
            return {
                "type": self.text,
                "param": (
                    self.sfx_workspace.parameters[0]
                    if self.sfx_workspace.parameters
                    else ""
                ),
            }

        # Handle case where params might be empty or None
        params = []
        if self.params:
            params = [opt for _, _, opts in self.params for opt in opts]

        precon_json = {
            "predicate": self.text,
            "params": params,
            "is_true": self.toggled,
        }
        return precon_json

    # in the case of special effect instead of regular predicate
    def serialize(self):
        return self.sfx_workspace.serialize()

    def _sync_params(self):
        # No parameter widgets to sync anymore
        pass

    def set_relative_position(self, pos):
        super().set_relative_position(pos)
        self._sync_params()

    def toggle_color(self):
        self.toggled = not self.toggled
        if self.toggled:
            self.colours["normal_bg"] = pygame.Color("darkgreen")
            self.colours["hovered_bg"] = pygame.Color("black")
        else:
            self.colours["normal_bg"] = pygame.Color("darkred")
            self.colours["hovered_bg"] = pygame.Color("black")
        self.rebuild()

    def process_event(self, event):
        handled = super().process_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.rect.collidepoint(event.pos):
                if self.docked_slot:
                    self.docked_slot.occupied = None
                    self.docked_slot = None
                self.is_dragging = True
                self.mouse_down_pos = event.pos
                abs_r = self.get_abs_rect()
                mx, my = event.pos
                self._drag_offset = (abs_r.x - mx, abs_r.y - my)
                return handled

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                self.unfocus()

                snapped = False
                
                # Check all workspaces for snap slots
                for ws in all_workspaces:
                    snap = ws.get_snap_slot(self.get_abs_rect())
                    if snap:
                        if not snap.hidden:
                            # dock into the new slot
                            if self.docked_slot:
                                self.docked_slot.occupied = None  # clear previous slot
                            snap.occupied = self
                            self.docked_slot = snap
                            block_slots[self.id] = snap

                            abs_slot_x = ws.get_abs_rect().x + snap.rel_pos[0]
                            abs_slot_y = ws.get_abs_rect().y + snap.rel_pos[1]

                            container_rect = self.ui_container.get_abs_rect()
                            rel_x = abs_slot_x - container_rect.x
                            rel_y = abs_slot_y - container_rect.y

                            self.set_relative_position((rel_x, rel_y))
                            snapped = True
                            ws.parametrize()
                            break
                
                # Check ObjectWorkspace predicate slots
                if not snapped:
                    for ws in all_workspaces:
                        if isinstance(ws, ObjectWorkspace):
                            predicate_slot = ws.get_predicate_snap_slot(self.get_abs_rect())
                            if predicate_slot:
                                # Dock into predicate slot
                                if self.docked_slot:
                                    self.docked_slot.occupied = None
                                predicate_slot.occupied = self
                                self.docked_slot = predicate_slot
                                block_slots[self.id] = predicate_slot

                                # Position relative to asset config container
                                abs_slot_x = ws.asset_config_container.get_abs_rect().x + predicate_slot.rel_pos[0]
                                abs_slot_y = ws.asset_config_container.get_abs_rect().y + predicate_slot.rel_pos[1]

                                container_rect = self.ui_container.get_abs_rect()
                                rel_x = abs_slot_x - container_rect.x
                                rel_y = abs_slot_y - container_rect.y

                                self.set_relative_position((rel_x, rel_y))
                                snapped = True
                                break

                if not snapped and self.docked_slot:
                    # undocked: clear previous slot
                    self.docked_slot.occupied = None
                    self.docked_slot = None
                    block_slots.pop(self.id, None)

                # small click toggles
                dx = abs(event.pos[0] - self.mouse_down_pos[0])
                dy = abs(event.pos[1] - self.mouse_down_pos[1])
                if dx < 5 and dy < 5 and not self.is_sfx:
                    self.toggle_color()
                if dx < 5 and dy < 5 and self.is_sfx and self.docked_slot:
                    rel_pos = (self.get_relative_rect()[0], self.get_relative_rect()[1])
                    self.sfx_workspace.set_relative_position((rel_pos[0], rel_pos[1]))

                    if self.sfx_workspace.hidden:
                        self.sfx_workspace.show()
                        self.sfx_workspace.preview_layer(4)
                    else:
                        self.sfx_workspace.hide()
                        
                for ws in all_workspaces:
                    if hasattr(ws, 'parametrize'):
                        ws.parametrize()
                return handled

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x, mouse_y = event.pos

            abs_new_x = mouse_x + self._drag_offset[0]
            abs_new_y = mouse_y + self._drag_offset[1]

            container_rect = (
                self.ui_container.get_abs_rect()
                if self.ui_container
                else pygame.Rect(0, 0, 0, 0)
            )

            rel_new_x = abs_new_x - container_rect.x
            rel_new_y = abs_new_y - container_rect.y

            self.set_relative_position((rel_new_x, rel_new_y))

        return handled

    #  tidy‑up when the block is killed
    def kill(self):
        # No parameter widgets to kill anymore
        block_slots.pop(self.id, None)
        blocks_by_id.pop(self.id, None)
        super().kill()

    def hide(self):
        super().hide()

    def show(self):
        super().show()


class EditorPanel(UIScrollingContainer):
    def __init__(
        self,
        relative_rect,
        manager,
        bg_color=pygame.Color("#E0F1F8"),
        starting_height=1,
        allow_scroll_x=True,
    ):
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            starting_height=starting_height,
            allow_scroll_x=allow_scroll_x,
        )
        self.background_colour = bg_color
        self.rebuild()
        self.showing_predicates = True


def _uniq(pred_list):
    """Return a list with duplicate predicate dicts removed."""
    seen = set()
    out = []
    for pr in pred_list:
        key = (pr["predicate"], tuple(pr["params"]), pr.get("is_true"))
        if key not in seen:
            seen.add(key)
            out.append(pr)
    return out


def _dedup_sfx(sfx_dict):
    """Emit each unique SFX exactly once."""
    key = json.dumps(sfx_dict, sort_keys=True)
    if key in _dedup_sfx._seen:
        return None
    _dedup_sfx._seen.add(key)
    return sfx_dict


_dedup_sfx._seen = set()


class ActionWorkspace(UIPanel):
    def __init__(
        self,
        relative_rect,
        manager,
        container=None,
        bg_color=pygame.Color("#DCEAF4"),
        text="",
        starting_height=1,
        parameters=set(),
        **kwargs,
    ):
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            starting_height=starting_height,
            **kwargs,
        )
        self.background_colour = bg_color
        self.rebuild()
        self.attached_blocks = []
        self.name = ""
        self.precons = []
        self.ifxs = []
        self.sfxs = []
        self.text = text
        self.parameters = parameters
        self.param_boxes = []
        self.manager = manager

        # TODO make a typable text box for this later

        self.slots = []

        self.top_label = UITextEntryBox(
            relative_rect=pygame.Rect(0, 0, self.relative_rect.w, 50),
            manager=manager,
            container=self,
            initial_text=self.text,
            placeholder_text="Enter your action name...",
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
            relative_rect=pygame.Rect(0, 450, 150, 50),
            manager=manager,
            container=self,
        )
        self.ex_button = UIButton(
            relative_rect=pygame.Rect(relative_rect.width - 160, 0, 80, 50),    
            text="Close",
            manager=manager,
            container=self,
            starting_height=2,
        )

        self.save_button = UIButton(
            relative_rect=pygame.Rect(relative_rect.width - 80, 0, 80, 50),   
            text="Save", 
            manager=manager,
            container=self,
            starting_height=2,
        )
        # ───── CONFIG ─────
        NUM_SLOTS = 8
        SLOT_W, SLOT_H = 185, 40
        MARGIN_X = 20  # px on left & right
        H_SPACING = 3  # horizontal gap
        V_SPACING = 10  # vertical gap

        # find how many fit per row
        ws_w = self.get_relative_rect().width
        avail = ws_w - 2 * MARGIN_X
        slots_per_row = max(1, int((avail + H_SPACING) // (SLOT_W + H_SPACING)))

        # recompute spacing so it's evenly spread
        if slots_per_row > 1:
            spacing_x = (avail - slots_per_row * SLOT_W) / (slots_per_row - 1)
        else:
            spacing_x = 0

        # Y‑coordinates under each label
        y_pre = self.preconditions_label.get_relative_rect().bottom + V_SPACING + 10
        y_ifx = self.immediateFX_label.get_relative_rect().bottom + V_SPACING + 10
        y_sfx = self.specialFX_label.get_relative_rect().bottom + V_SPACING + 10

        # build wrapped rows for each section
        counter = 0
        for base_y in (y_pre, y_ifx, y_sfx):
            for i in range(NUM_SLOTS):
                counter += 1
                row, col = divmod(i, slots_per_row)
                x = MARGIN_X + col * (SLOT_W + spacing_x)
                y = base_y + row * (SLOT_H + V_SPACING)
                if counter < 9:
                    section = "preconditions"
                elif counter < 17:
                    section = "ifx"
                else:
                    section = "sfx"

                self.slots.append(Slot((int(x), y), section=section))

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.save_button:
                action = self.serialize()
                # print(action)
                # json.dump(action, out_file, indent=4)
            elif event.ui_element == self.ex_button:
                self.kill()

        return handled

    def preview_layer(self, top_layer):
        self.change_layer(top_layer)
        for child in self.get_container().elements:
            child.change_layer(top_layer + 1)
        for slot in self.slots:
            if slot.occupied != None:
                slot.occupied.change_layer(top_layer + 1)

    def kill(self):
        if self in all_workspaces:
            all_workspaces.remove(self)

        for slot in self.slots:
            if slot.occupied != None:
                slot.occupied.kill()

        self.slots.clear()
        super().kill()

    def draw_debug_slots(self, surf):
        for slot in self.slots:
            abs_x = self.get_abs_rect().x + slot.rel_pos[0]
            abs_y = self.get_abs_rect().y + slot.rel_pos[1]
            pygame.draw.rect(
                surf,
                (
                    pygame.Color("gray")
                    if slot.occupied is None
                    else pygame.Color("darkgreen")
                ),
                pygame.Rect((abs_x, abs_y), slot.size),
                2,
            )

    def parametrize(self):
        for box in self.param_boxes:
            box.kill()

        self.parameters.clear()
        self.param_boxes.clear()

        for i, slot in enumerate(self.slots):
            if slot.occupied is None:
                continue

            block = slot.occupied

            # Only process parameters if they exist (for backwards compatibility)
            if block.params:
                for label, pos, opts in block.params:
                    self.parameters.update(opts)

        for i, param in enumerate(self.parameters):
            if param[0] == "i":
                obj_id = "#item"
            elif param[0] == "s":
                obj_id = "#station"
            elif param[0] == "p":
                obj_id = "#player"
            elif param[0] == "c":
                obj_id = "#container"
            else:
                obj_id = "#meal"

            param_box = UITextBox(
                html_text="<font color=#FFFFFF>" + param + "</font>",
                relative_rect=pygame.Rect(485 - i * 50, 0, 50, 50),
                manager=self.manager,
                container=self,
                object_id=ObjectID(class_id="@parameter_boxes", object_id=obj_id),
            )
            self.param_boxes.append(param_box)

    def get_snap_slot(self, block_abs_rect):
        """Return a free Slot whose (inflated) rect contains block centre, else None."""
        cx, cy = block_abs_rect.center
        for slot in self.slots:
            if slot.occupied is None and not slot.hidden:
                big = slot.rect()
                big = big.inflate(SNAP_TOLERANCE, SNAP_TOLERANCE)
                # convert slot rect to ABSOLUTE coords:
                abs_slot = big.move(self.get_abs_rect().topleft)
                if abs_slot.collidepoint(cx, cy):
                    return slot
        return None

    # used for adding block during loading of action from json
    def attach_block(self, block: DraggableBlock, slot: Slot):
        # same docking logic from block process event
        block_slots[block.id] = slot

        abs_slot_x = self.get_abs_rect().x + slot.rel_pos[0]
        abs_slot_y = self.get_abs_rect().y + slot.rel_pos[1]

        # now get this block's container (still center_panel)
        container_rect = block.ui_container.get_abs_rect()

        # set rel position inside that panel, calculated from abs position
        rel_x = abs_slot_x - container_rect.x
        rel_y = abs_slot_y - container_rect.y

        slot.occupied = block
        block.slot_section = slot

        block.set_relative_position((rel_x, rel_y))

    def calculate_slots(self):
        self.precons, self.ifxs, self.sfxs = [], [], []

        for slot in self.slots:
            if slot.occupied is None:
                continue
            block = slot.occupied
            sect = slot.section
            if sect == "preconditions":
                self.precons.append(block)
            elif sect == "ifx":
                self.ifxs.append(block)
            else:
                self.sfxs.append(block)

    def serialize(self):
        self.calculate_slots()
        raw_sfx = [b.serialize() for b in self.sfxs]
        unique_sfx = []
        for entry in raw_sfx:
            deduped = _dedup_sfx(entry)
            if deduped is not None:
                unique_sfx.append(deduped)
        action = {
            "name": self.top_label.get_text(),
            "precons": _uniq([b.to_json() for b in self.precons]),
            "immediate_fx": _uniq([b.to_json() for b in self.ifxs]),
            "sfx": unique_sfx,
            "language_description": "",
        }
        print(action)
        return action


class AssetConfigSlot:
    """A slot for configuring an asset with predicates"""
    
    def __init__(self, rel_pos, size, manager, container, workspace):
        self.rel_pos = rel_pos
        self.size = size
        self.manager = manager
        self.container = container
        self.workspace = workspace
        self.occupied = False
        
        # Asset configuration data
        self.asset_name = ""
        self.file_path = ""
        self.predicate_slots = []  # List of PredicateSlot objects
        
        # UI elements
        self.ui_elements = []
        
    def configure_asset(self, asset_name, file_path):
        """Configure this slot with an asset"""
        self.asset_name = asset_name
        self.file_path = file_path
        self.occupied = True
        
        # Create UI elements for this slot
        self.create_ui_elements()
        
    def create_ui_elements(self):
        """Create UI elements for asset configuration"""
        x, y = self.rel_pos
        
        # Asset name entry
        name_entry = UITextEntryBox(
            relative_rect=pygame.Rect(x, y, 100, 30),
            manager=self.manager,
            container=self.container,
            initial_text=self.asset_name,
            placeholder_text="Asset name..."
        )
        self.ui_elements.append(name_entry)
        
        # Image thumbnail instead of filename
        if self.file_path and os.path.exists(self.file_path):
            try:
                # Load and scale the image to thumbnail size
                original_image = pygame.image.load(self.file_path).convert_alpha()
                
                # Scale to thumbnail size (e.g., 60x60)
                thumb_size = 60
                original_w, original_h = original_image.get_size()
                
                # Calculate scaling to maintain aspect ratio
                if original_w > original_h:
                    scale = thumb_size / original_w
                else:
                    scale = thumb_size / original_h
                    
                new_w = max(1, int(original_w * scale))
                new_h = max(1, int(original_h * scale))
                
                thumbnail = pygame.transform.scale(original_image, (new_w, new_h))
                
                # Create UIImage with thumbnail
                image_element = UIImage(
                    relative_rect=pygame.Rect(x + 110, y, thumb_size, thumb_size),
                    image_surface=thumbnail,
                    manager=self.manager,
                    container=self.container,
                )
                self.ui_elements.append(image_element)
                
            except Exception as e:
                # Fallback to filename if image loading fails
                filename = os.path.basename(self.file_path)
                file_label = UITextBox(
                    html_text=f"<font color=#000000>{filename}</font>",
                    relative_rect=pygame.Rect(x + 110, y, 120, 30),
                    manager=self.manager,
                    container=self.container,
                )
                self.ui_elements.append(file_label)
                print(f"Error loading image thumbnail: {e}")
        else:
            # No file or file doesn't exist
            file_label = UITextBox(
                html_text="<font color=#000000>No file</font>",
                relative_rect=pygame.Rect(x + 110, y, 120, 30),
                manager=self.manager,
                container=self.container,
            )
            self.ui_elements.append(file_label)
    
        pred_label = UITextBox(
            html_text="<font color=#000000>Predicates:</font>",
            relative_rect=pygame.Rect(x, y + 70, 80, 25),
            manager=self.manager,
            container=self.container,
        )
        self.ui_elements.append(pred_label)
        
        # Create predicate slots (up to 4 slots per asset config)
        self.predicate_slots = []
        for i in range(4):
            slot_x = x + 80 + (i * 125)  # Spread them out horizontally
            slot_y = y + 70  # More space below thumbnails
            pred_slot = PredicateSlot((slot_x, slot_y), self)
            self.predicate_slots.append(pred_slot)
        
        # Remove button - positioned better relative to thumbnail
        remove_btn = UIButton(
            relative_rect=pygame.Rect(x + 210, y + 15, 30, 25),
            text="X",
            manager=self.manager,
            container=self.container,
        )
        self.ui_elements.append(remove_btn)
        
        # Store references for event handling
        self.name_entry = name_entry
        self.remove_btn = remove_btn
        
    def get_predicates(self):
        """Get list of predicate names from docked blocks"""
        predicates = []
        for pred_slot in self.predicate_slots:
            if pred_slot.occupied:
                predicates.append(pred_slot.occupied.text)
        return predicates
        
    def update_from_ui(self):
        """Update slot data from UI elements"""
        if hasattr(self, 'name_entry'):
            self.asset_name = self.name_entry.get_text()
    
    def cleanup(self):
        """Clean up UI elements and predicate blocks"""
        # Kill any docked predicate blocks
        for pred_slot in self.predicate_slots:
            if pred_slot.occupied:
                pred_slot.occupied.kill()
                pred_slot.occupied = None
        
        # Kill UI elements
        for element in self.ui_elements:
            element.kill()
        self.ui_elements.clear()
        self.predicate_slots.clear()


class ObjectWorkspace(UIPanel):
    def __init__(
        self,
        relative_rect,
        manager,
        container=None,
        bg_color=pygame.Color("#DCEAF4"),
        text="",
        **kwargs,
    ):
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            starting_height=1,
            **kwargs,
        )
        self.text = text
        self.background_colour = bg_color
        self.rebuild()
        self.attached_blocks = []
        self.manager = manager
        self.loaded_assets = []
        self.asset_ui_elements = []
        
        # New: asset configurations with predicates
        self.asset_configs = {}  # {"asset_name": {"file": "path.png", "predicates": ["pred1", "pred2"]}}

        self.slots = []

        self.top_label = UITextEntryBox(
            relative_rect=pygame.Rect(0, 0, self.relative_rect.w, 50),
            manager=manager,
            container=self,
            initial_text=self.text,
            placeholder_text="Enter your object name...",
        )

        self.type_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Object Type: item</b></font>",
            relative_rect=pygame.Rect(0, 50, 200, 50),
            manager=manager,
            container=self,
        )

        # Default object type to "item" - no dropdown needed
        self.object_type = "item"

        # Asset configuration section
        self.asset_config_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Asset Configurations:</b></font>",
            relative_rect=pygame.Rect(0, 100, 200, 50),
            manager=manager,
            container=self,
        )

        self.asset_config_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 150, self.relative_rect.w, 400),
            manager=manager,
            container=self,
            allow_scroll_x=False,
            allow_scroll_y=True,
        )

        self.add_asset_config_button = UIButton(
            relative_rect=pygame.Rect(200, 100, 150, 50),
            text="Add Asset Config",
            manager=manager,
            container=self,
            starting_height=2,
        )

        # Create slots for asset configurations
        self.create_asset_slots()

        self.ex_button = UIButton(
            relative_rect=pygame.Rect(500, 0, 80, 50),
            text="Close",
            manager=manager,
            container=self,
            starting_height=2,
        )
        self.save_button = UIButton(
            relative_rect=pygame.Rect(580, 0, 80, 50),
            text="Save",
            manager=manager,
            container=self,
            starting_height=2,
        )

    def create_asset_slots(self):
        """Create slots for asset configurations"""
        NUM_SLOTS = 10
        SLOT_W, SLOT_H = 600, 130  # Increased height to fit predicates properly
        MARGIN_X = 10
        V_SPACING = 10

        for i in range(NUM_SLOTS):
            y = i * (SLOT_H + V_SPACING) + 10
            slot = AssetConfigSlot(
                rel_pos=(MARGIN_X, y),
                size=(SLOT_W, SLOT_H),
                manager=self.manager,
                container=self.asset_config_container,
                workspace=self
            )
            self.slots.append(slot)

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.add_asset_config_button:
                self.add_new_asset_config()
            elif event.ui_element == self.ex_button:
                self.kill()
            elif event.ui_element == self.save_button:
                self.save_to_config()

        return handled

    def add_new_asset_config(self):
        """Add a new asset configuration"""
        file_path = open_file_dialog(
            title="Select Asset File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*"),
            ],
        )

        if file_path and os.path.exists(file_path):
            # Find an empty slot
            for slot in self.slots:
                if not slot.occupied:
                    asset_name = os.path.splitext(os.path.basename(file_path))[0]
                    slot.configure_asset(asset_name, file_path)
                    break

    def get_predicate_snap_slot(self, block_abs_rect):
        """Return a free PredicateSlot whose rect contains block center, else None."""
        cx, cy = block_abs_rect.center
        
        for asset_slot in self.slots:
            if asset_slot.occupied:  # Only check slots that have assets
                for pred_slot in asset_slot.predicate_slots:
                    if pred_slot.occupied is None and not pred_slot.hidden:
                        big = pred_slot.rect()
                        big = big.inflate(SNAP_TOLERANCE, SNAP_TOLERANCE)
                        # Convert to absolute coords relative to asset config container
                        abs_slot = big.move(self.asset_config_container.get_abs_rect().topleft)
                        if abs_slot.collidepoint(cx, cy):
                            return pred_slot
        return None

    def save_to_config(self):
        """Save object to robotouille_config.json"""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "renderer", "configuration", "robotouille_config.json"
        )
        config_path = os.path.normpath(config_path)
        
        # Load existing config or create new one
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            config_data = {"version": "1.0.1"}
        
        # Use hardcoded object type
        object_type = self.object_type
        object_name = self.top_label.get_text().lower()
        
        if not object_name:
            print("Error: Object name is required")
            return
            
        # Initialize object type section if it doesn't exist
        if object_type not in config_data:
            config_data[object_type] = {
                "constants": {},
                "entities": {}
            }
        
        # Build the object configuration
        object_config = self.serialize_for_config()
        
        # Add to config
        config_data[object_type]["entities"][object_name] = object_config
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        
        print(f"Object '{object_name}' saved to config: {config_path}")

    def serialize_for_config(self):
        """Serialize object for config file format"""
        assets = {}
        constants = {}
        
        # Process asset configurations from slots
        default_set = False
        for slot in self.slots:
            if slot.occupied and slot.asset_name and slot.file_path:
                asset_filename = os.path.basename(slot.file_path)
                predicates = slot.get_predicates()
                
                if slot.asset_name.lower() == "default" or not default_set:
                    # This is the default asset
                    assets["default"] = asset_filename
                    default_set = True
                else:
                    # This is a conditional asset
                    asset_config = {
                        "asset": asset_filename
                    }
                    
                    # Add predicates if any
                    if predicates:
                        asset_config["predicates"] = predicates
                    
                    assets[slot.asset_name] = asset_config
        
        return {
            "assets": assets,
            "constants": constants
        }

    def parametrize(self):
        pass

    def get_snap_slot(self, block_abs_rect):
        # ObjectWorkspace doesn't use regular snap slots, only predicate slots
        return None

    def kill(self):
        if self in all_workspaces:
            all_workspaces.remove(self)

        # Clean up asset config slots
        for slot in self.slots:
            slot.cleanup()
        self.slots.clear()
        
        super().kill()

    def draw_debug_slots(self, surf):
        """Draw debug visualization for asset config slots and predicate slots"""
        for slot in self.slots:
            if slot.occupied:
                # Draw asset config slot border
                abs_x = self.asset_config_container.get_abs_rect().x + slot.rel_pos[0]
                abs_y = self.asset_config_container.get_abs_rect().y + slot.rel_pos[1]
                color = pygame.Color("lightblue")
                pygame.draw.rect(
                    surf,
                    color,
                    pygame.Rect((abs_x, abs_y), slot.size),
                    2,
                )
                
                # Draw predicate slots
                for pred_slot in slot.predicate_slots:
                    pred_abs_x = self.asset_config_container.get_abs_rect().x + pred_slot.rel_pos[0]
                    pred_abs_y = self.asset_config_container.get_abs_rect().y + pred_slot.rel_pos[1]
                    pred_color = pygame.Color("lightgreen") if pred_slot.occupied else pygame.Color("lightgray")
                    pygame.draw.rect(
                        surf,
                        pred_color,
                        pygame.Rect((pred_abs_x, pred_abs_y), pred_slot.size),
                        2,
                    )


class PredicateCreator(UIPanel):
    def __init__(
        self,
        relative_rect,
        manager,
        container=None,
        bg_color=pygame.Color("#DCEAF4"),
        **kwargs,
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
        self.manager = manager

        self.top_label = UITextEntryBox(
            relative_rect=pygame.Rect(0, 0, self.relative_rect.w, 50),
            manager=manager,
            container=self,
            initial_text="",
            placeholder_text="Enter your predicate name...",
        )

        self.options = ["none", "item", "station", "player", "container", "meal"]

        self.first_param = UIDropDownMenu(
            options_list=self.options,
            starting_option=self.options[0],
            relative_rect=pygame.Rect(relative_rect.x, relative_rect.y + 50, 100, 50),
            manager=manager,
            container=self.ui_container,
        )

        self.second_param = UIDropDownMenu(
            options_list=self.options,
            starting_option=self.options[0],
            relative_rect=pygame.Rect(
                relative_rect.x + 100, relative_rect.y + 50, 100, 50
            ),
            manager=manager,
            container=self.ui_container,
        )

        def serialize(self):
            name = self.top_label.get_text()
            param1, param2 = (
                self.first_param.selected_option,
                self.second_param.selected_option,
            )
            params = [p for p in (param1, param2) if p.lower() != "none"]

            return {
                "name": name,
                "param_types": params,
                "language_descriptors": {"0": ""},
            }

        # def get_snap_slot(self, block_abs_rect):
        #     pass

    def parametrize(self):
        """Returns parameter list to be used for DraggableBlock creation"""
        # Handle both string and tuple returns from dropdown
        param1_option = self.first_param.selected_option
        param2_option = self.second_param.selected_option
        
        param1 = param1_option[0] if isinstance(param1_option, tuple) else param1_option
        param2 = param2_option[0] if isinstance(param2_option, tuple) else param2_option

        params = [p for p in [param1, param2] if p != "none"]
        i, s, p, c, m = 1, 1, 1, 1, 1

        param_list = []
        for param_type in params:
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

        return param_list

    def serialize(self):
        name = self.top_label.get_text()
        # Handle both string and tuple returns from dropdown
        param1_option = self.first_param.selected_option
        param2_option = self.second_param.selected_option
        
        param1 = param1_option[0] if isinstance(param1_option, tuple) else param1_option
        param2 = param2_option[0] if isinstance(param2_option, tuple) else param2_option

        params = [p for p in [param1, param2] if p != "none"]

        return {
            "name": name,
            "param_types": params,
            "language_descriptors": {"0": ""},
        }

    def kill(self):
        if self in all_workspaces:
            all_workspaces.remove(self)

        # # for asset_element in self.asset_ui_elements:
        # #     asset_element.kill()
        # self.asset_ui_elements.clear()
        self.first_param.kill()
        self.second_param.kill()
        super().kill()

    def get_snap_slot(self, block_abs_rect):
        # PredicateCreator doesn't have snap slots
        return None


class SFXWorkspace(UIPanel):
    def __init__(
        self,
        relative_rect,
        manager,
        container=None,
        bg_color=pygame.Color(30, 0, 93),
        text="",
        starting_height=1,
        parameters=[],
        **kwargs,
    ):
        super().__init__(
            relative_rect=relative_rect,
            manager=manager,
            container=container,
            starting_height=starting_height,
            **kwargs,
        )
        self.background_colour = bg_color
        self.rebuild()
        self.attached_blocks = []
        self.name = text
        self.parameters = parameters
        self.param_boxes = []
        self.manager = manager

        self.hidden = False
        self.block = None

        self.precons = []
        self.ifxs = []
        self.sfx = []

        self.type = {"conditional", "repetitive", "delayed"}

        self.slots = []

        self.label = UITextBox(
            html_text="<font color=#FFFFFF><b>" + self.name + "</b></font>",
            relative_rect=pygame.Rect(0, 0, self.relative_rect.w, 50),
            manager=manager,
            container=self,
        )
        self.ex_button = UIButton(
            relative_rect=pygame.Rect(690, 0, 80, 50),
            text="Close",
            manager=manager,
            container=self,
            starting_height=2,
        )

        # ───── CONFIG ───── (SIMILAR TO ACTIONWORKSPACE)
        NUM_SLOTS = 8
        SLOT_W, SLOT_H = 185, 40
        MARGIN_X = 20  # px on left & right
        H_SPACING = 3  # horizontal gap
        V_SPACING = 10  # vertical gap

        # find how many fit per row
        ws_w = self.get_relative_rect().width
        avail = ws_w - 2 * MARGIN_X
        slots_per_row = max(1, int((avail + H_SPACING) // (SLOT_W + H_SPACING)))

        # recompute spacing so it's evenly spread
        if slots_per_row > 1:
            spacing_x = (avail - slots_per_row * SLOT_W) / (slots_per_row - 1)
        else:
            spacing_x = 0

        if text == "conditional" and text in self.type:
            self.preconditions_label = UITextBox(
                html_text="<font color=#FFFFFF><b>Conditions</b></font>",
                relative_rect=pygame.Rect(0, 50, 150, 50),
                manager=manager,
                container=self,
            )

            self.immediateFX_label = UITextBox(
                html_text="<font color=#FFFFFF><b>FX</b></font>",
                relative_rect=pygame.Rect(0, 250, 150, 50),
                manager=manager,
                container=self,
            )

            self.specialFX_label = UITextBox(
                html_text="<font color=#FFFFFF><b>Special FX</b></font>",
                relative_rect=pygame.Rect(0, 450, 150, 50),
                manager=manager,
                container=self,
            )
            y_pre = self.preconditions_label.get_relative_rect().bottom + V_SPACING + 10
            y_ifx = self.immediateFX_label.get_relative_rect().bottom + V_SPACING + 10
            y_sfx = self.specialFX_label.get_relative_rect().bottom + V_SPACING + 10
            counter = 0
            for base_y in (y_pre, y_ifx, y_sfx):
                for i in range(NUM_SLOTS):
                    counter += 1
                    row, col = divmod(i, slots_per_row)
                    x = MARGIN_X + col * (SLOT_W + spacing_x)
                    y = base_y + row * (SLOT_H + V_SPACING)
                    if counter < 9:
                        section = "preconditions"
                    elif counter < 17:
                        section = "ifx"
                    else:
                        section = "sfx"

                    self.slots.append(Slot((int(x), y), section=section))
                    self.slots[-1].workspace = self

        elif (text == "repetitive" or text == "delayed") and text in self.type:
            self.immediateFX_label = UITextBox(
                html_text="<font color=#FFFFFF><b>FX</b></font>",
                relative_rect=pygame.Rect(0, 50, 150, 50),
                manager=manager,
                container=self,
            )

            self.specialFX_label = UITextBox(
                html_text="<font color=#FFFFFF><b>Special FX</b></font>",
                relative_rect=pygame.Rect(0, 250, 150, 50),
                manager=manager,
                container=self,
            )
            y_ifx = self.immediateFX_label.get_relative_rect().bottom + V_SPACING + 10
            y_sfx = self.specialFX_label.get_relative_rect().bottom + V_SPACING + 10
            counter = 0
            for base_y in (y_ifx, y_sfx):
                for i in range(NUM_SLOTS):
                    counter += 1
                    row, col = divmod(i, slots_per_row)
                    x = MARGIN_X + col * (SLOT_W + spacing_x)
                    y = base_y + row * (SLOT_H + V_SPACING)
                    if counter < 9:
                        section = "ifx"
                    else:
                        section = "sfx"
                    self.slots.append(Slot((int(x), y), section=section))

        else:
            raise Exception("Bad label: invalid special effect")

    def draw_debug_slots(self, surf):
        for slot in self.slots:
            abs_x = self.get_abs_rect().x + slot.rel_pos[0]
            abs_y = self.get_abs_rect().y + slot.rel_pos[1]
            pygame.draw.rect(
                surf,
                (
                    pygame.Color("gray")
                    if slot.occupied is None
                    else pygame.Color("darkgreen")
                ),
                pygame.Rect((abs_x, abs_y), slot.size),
                4,
            )

    def attach_block(self, block: DraggableBlock, slot: Slot):
        # same docking logic from block process event
        block_slots[block.id] = slot

        abs_slot_x = self.get_abs_rect().x + slot.rel_pos[0]
        abs_slot_y = self.get_abs_rect().y + slot.rel_pos[1]

        # now get this block's container (still center_panel)
        container_rect = block.ui_container.get_abs_rect()

        # set rel position inside that panel, calculated from abs position
        rel_x = abs_slot_x - container_rect.x
        rel_y = abs_slot_y - container_rect.y

        slot.occupied = block
        block.slot_section = slot

        block.set_relative_position((rel_x, rel_y))

    def process_event(self, event: pygame.Event) -> bool:
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ex_button:
                if self.block:
                    self.block.kill()
                self.kill()

        return handled

    def associate_block(self, block: DraggableBlock):
        self.block = block

    def preview_layer(self, top_layer):
        self.change_layer(top_layer)
        for child in self.get_container().elements:
            child.change_layer(top_layer + 1)
        for slot in self.slots:
            if slot.occupied != None:
                slot.occupied.change_layer(top_layer + 1)

    def kill(self):
        if self in all_workspaces:
            all_workspaces.remove(self)

        for slot in self.slots:
            if slot.occupied != None:
                slot.occupied.kill()

        self.slots.clear()
        super().kill()

    def calculate_slots(self):
        self.precons, self.ifxs, self.sfxs = [], [], []

        for slot in self.slots:
            if slot.occupied is None:
                continue
            block = slot.occupied
            sect = slot.section
            if sect == "preconditions":
                self.precons.append(block)
            elif sect == "ifx":
                self.ifxs.append(block)
            else:
                self.sfxs.append(block)

    def serialize(self):
        self.calculate_slots()
        self.parametrize()
        param = self.parameters[0] if self.parameters else ""
        raw_sfx = [b.to_json() for b in self.sfxs]
        unique_sfx = []
        for entry in raw_sfx:
            deduped = _dedup_sfx(entry)
            if deduped is not None:
                unique_sfx.append(deduped)

        if self.name == "conditional":
            sfx = {
                "type": self.name,
                "param": param,
                "conditions": _uniq([b.to_json() for b in self.precons]),
                "fx": _uniq([b.to_json() for b in self.ifxs]),
                "sfx": unique_sfx,
            }
        else:
            sfx = {
                "type": self.name,
                "param": param,
                "fx": _uniq([b.to_json() for b in self.ifxs]),
                "sfx": unique_sfx,
            }
        return sfx

    def get_snap_slot(self, block_abs_rect):
        """Return a free Slot whose (inflated) rect contains block centre, else None."""
        cx, cy = block_abs_rect.center
        for slot in self.slots:
            if slot.occupied is None and not slot.hidden:
                big = slot.rect()
                big = big.inflate(SNAP_TOLERANCE, SNAP_TOLERANCE)
                # convert slot rect to ABSOLUTE coords:
                abs_slot = big.move(self.get_abs_rect().topleft)
                if abs_slot.collidepoint(cx, cy):
                    return slot
        return None

    def hide(self):
        for slot in self.slots:
            slot.hide()
            if slot.occupied != None:
                slot.occupied.hide()

        self.hidden = True
        super().hide()

    def show(self):
        for slot in self.slots:
            slot.show()
            if slot.occupied != None:
                slot.occupied.show()
        self.hidden = False
        super().show()

    def parametrize(self):
        for box in self.param_boxes:
            box.kill()

        self.parameters.clear()
        self.param_boxes.clear()

        for i, slot in enumerate(self.slots):
            if slot.occupied is None:
                continue

            block = slot.occupied

            
            if block.params:
                for label, pos, opts in block.params:
                    for opt in opts:
                        if opt not in self.parameters:
                            self.parameters.append(opt)

        for i, param in enumerate(self.parameters):
            if param[0] == "i":
                obj_id = "#item"
            elif param[0] == "s":
                obj_id = "#station"
            elif param[0] == "p":
                obj_id = "#player"
            elif param[0] == "c":
                obj_id = "#container"
            else:
                obj_id = "#meal"

            param_box = UITextBox(
                html_text="<font color=#FFFFFF>" + param + "</font>",
                relative_rect=pygame.Rect(485 - i * 50, 0, 50, 50),
                manager=self.manager,
                container=self,
                object_id=ObjectID(class_id="@parameter_boxes", object_id=obj_id),
            )
            self.param_boxes.append(param_box)
