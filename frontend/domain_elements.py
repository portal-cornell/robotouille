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

    def rect(self):
        return pygame.Rect(self.rel_pos, self.size)

    # for debugging
    def show_section(self):
        print(self.section)


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

        #  create & memorise each param dropdown
        self._param_widgets = []  # list of (offset, widget)
        for label, pos, options in param_defs or []:
            dd_rect = pygame.Rect(
                relative_rect.x + pos[0] + 25, relative_rect.y + pos[1] - 10, 50, 30
            )
            dd = UIDropDownMenu(
                options_list=options,
                starting_option=options[0],
                relative_rect=dd_rect,
                manager=manager,
                container=self.ui_container,
            )

            # real offset = menu-topleft minus block-topleft
            offset = pygame.Vector2(dd_rect.topleft) - pygame.Vector2(
                relative_rect.topleft
            )

            if len(options) > 1:
                dd2_rect = pygame.Rect(
                    relative_rect.x + pos[0] - 25, relative_rect.y + pos[1] - 10, 50, 30
                )
                dd2 = UIDropDownMenu(
                    options_list=options,
                    starting_option=options[1],
                    relative_rect=dd2_rect,
                    manager=manager,
                    container=self.ui_container,
                )
                second_offset = pygame.Vector2(dd2_rect.topleft) - pygame.Vector2(
                    relative_rect.topleft
                )
                self._param_widgets.append((second_offset, dd2))
            self._param_widgets.append((offset, dd))
        self.params = param_defs
        # drag state
        self.is_dragging = False
        self._drag_offset = (0, 0)
        self.docked_slot = None
        self.toggled = is_true

        self.slot_section = None
        global current_id
        self.id = current_id
        current_id += 1
        blocks_by_id[self.id] = self

    def to_json(self):
        precon_json = {}
        precon_json["predicate"] = self.text
        precon_json["params"] = []
        for param in self.params:
            precon_json["params"].append(param[2])
        precon_json["is_true"] = self.toggled
        return precon_json

    def _sync_params(self):
        abs_tl = self.get_abs_rect().topleft
        for offset, widget in self._param_widgets:
            new_pos = (abs_tl[0] + offset.x, abs_tl[1] + offset.y)
            widget.set_position(new_pos)

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
                for ws in all_workspaces:
                    snap = ws.get_snap_slot(self.get_abs_rect())
                    if snap:
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

                if not snapped and self.docked_slot:
                    # undocked: clear previous slot
                    self.docked_slot.occupied = None
                    self.docked_slot = None
                    block_slots.pop(self.id, None)
                    print(all_workspaces)

                # small click toggles
                dx = abs(event.pos[0] - self.mouse_down_pos[0])
                dy = abs(event.pos[1] - self.mouse_down_pos[1])
                if dx < 5 and dy < 5:
                    self.toggle_color()
                for ws in all_workspaces:
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
        for _, widget in self._param_widgets:
            widget.kill()
        block_slots.pop(self.id, None)
        blocks_by_id.pop(self.id, None)
        super().kill()


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
            relative_rect=pygame.Rect(690, 0, 80, 50),
            text="Close",
            manager=manager,
            container=self,
            starting_height=2,
        )

        self.save_button = UIButton(
            relative_rect=pygame.Rect(770, 0, 80, 50),
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

        # recompute spacing so it’s evenly spread
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
                print(action)
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
            else:
                block = slot.occupied

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
            if slot.occupied is None:
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

        for block_id, slot in block_slots.items():
            block = blocks_by_id.get(block_id)
            if not block:  # block was killed, ignore
                continue

            sect = slot.section
            if sect == "preconditions":
                self.precons.append(block)
            elif sect == "ifx":
                self.ifxs.append(block)
            else:
                self.sfxs.append(block)

    def serialize(self):
        self.calculate_slots()
        action = {
            "name": self.top_label.get_text(),
            "precons": [b.to_json() for b in self.precons],
            "immediate_fx": [b.to_json() for b in self.ifxs],
            "sfx": [b.to_json() for b in self.sfxs],
            "language_description": "",
        }
        return action


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

        self.slots = []

        self.top_label = UITextEntryBox(
            relative_rect=pygame.Rect(0, 0, self.relative_rect.w, 50),
            manager=manager,
            container=self,
            initial_text=self.text,
            placeholder_text="Enter your object name...",
        )

        self.type_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Object Type:</b></font>",
            relative_rect=pygame.Rect(0, 50, 150, 50),
            manager=manager,
            container=self,
        )

        self.object_type_dd = UIDropDownMenu(
            options_list=["Item", "Station", "Container", "Meal"],
            starting_option="Item",
            relative_rect=pygame.Rect(150, 50, 150, 50),
            manager=manager,
            container=self,
        )
        # some of these are to make the assets look nicer, they're not used yet

        self.assets_label = UITextBox(
            html_text="<font color=#FFFFFF><b>Assets:</b></font>",
            relative_rect=pygame.Rect(0, 100, 150, 50),
            manager=manager,
            container=self,
        )

        self.assets_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 150, self.relative_rect.w, 400),
            manager=manager,
            container=self,
            allow_scroll_x=True,
            allow_scroll_y=True,
        )

        self.upload_button = UIButton(
            relative_rect=pygame.Rect(150, 100, 115, 50),
            text="Upload asset",
            manager=manager,
            container=self,
            starting_height=2,
        )

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

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.upload_button:
            
                file_path = open_file_dialog(
                    title="Select Asset File",
                    filetypes=[
                        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                        ("All files", "*.*"),
                    ],
                )

                if file_path and os.path.exists(file_path):
                    print(f"Selected file: {file_path}")
                    self.load_asset(file_path)
                elif file_path:
                    print(f"File not found: {file_path}")
              
#TODO: DO SOMETHING THAT DOENS'T JUST KILL ITSELF
            elif event.ui_element == self.ex_button:
                self.kill()
            elif event.ui_element == self.save_button:
                object_data = self.serialize()
                print("Object saved:", object_data)

        return handled

    def parametrize():
        pass

    # def load_asset(self, file_path):
    #     """Load and display an asset image"""
    #     try:
    #         # TODO: get this actaully working.
    #         image_surface = pygame.image.load(file_path).convert_alpha()

    #         max_size = 100
    #         width, height = image_surface.get_size()
    #         if width > height:
    #             scale = max_size / width
    #         else:
    #             scale = max_size / height

    #         new_width = int(width * scale)
    #         new_height = int(height * scale)
    #         image_surface = pygame.transform.scale(image_surface, (new_width, new_height))

    #         x_offset = 10 + (len(self.asset_ui_elements) % 5) * (max_size + 10)
    #         y_offset = 10 + (len(self.asset_ui_elements) // 5) * (max_size + 10)

    #         # create UIImage to display the asset
    #         image_element = UIImage(
    #             relative_rect=pygame.Rect(x_offset, y_offset, new_width, new_height),
    #             image_surface=image_surface,
    #             manager=self.manager,
    #             container=self.assets_container
    #         )

    #         self.loaded_assets.append(file_path)
    #         self.asset_ui_elements.append(image_element)

    #         #scrolling
    #         rows = (len(self.asset_ui_elements) + 4) // 5
    #         self.assets_container.set_scrollable_area_dimensions(
    #             (self.assets_container.relative_rect.width, max(400, rows * (max_size + 10) + 20))
    #         )

    #     except Exception as e:
    #         print(f"Error loading asset: {e}")
    def scale_img(self, image_surface, max_size):
        
        width, height = image_surface.get_size()
        # scaling
        if width > height:
            scale = max_size / width
        else:
            scale = max_size / height
            
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        return pygame.transform.scale(image_surface, (new_width, new_height))
       
    def load_asset(self, file_path):
        
        # load it and scale
        og_image = pygame.image.load(file_path).convert_alpha()
        max_size = 100
        scaled_img = self.scale_img(og_image, max_size)
        new_w, new_h = scaled_img.get_size()
        
        # position for the new image in the container grid
        x_offset = 10 + (len(self.asset_ui_elements) % 5) * (max_size + 10)
        y_offset = 10 + (len(self.asset_ui_elements) // 5) * (max_size + 10)
        
        # make python UIimage container to display the image
        image_element = UIImage(
            relative_rect=pygame.Rect(x_offset, y_offset, new_w, new_h),
            image_surface=scaled_img,
            manager=self.manager,
            container=self.assets_container
        )
        self.loaded_assets.append(file_path)
        self.asset_ui_elements.append(image_element)
        
        #TODO: a scrollable if we have an overflow
        
        print(f"Asset loaded: {file_path}")
      
       
    def get_snap_slot(self, block_abs_rect):
        pass

    def kill(self):
        if self in all_workspaces:
            all_workspaces.remove(self)

        # Clean up asset UI elements
        for asset_element in self.asset_ui_elements:
            asset_element.kill()
        self.asset_ui_elements.clear()

        for slot in self.slots:
            if slot.occupied != None:
                slot.occupied.kill()

        self.slots.clear()
        super().kill()

    def get_loaded_assets(self):
        """Return list of loaded asset file paths"""
        return self.loaded_assets

    def serialize(self):
        """Serialize the object workspace data"""
        return {
            "name": self.top_label.get_text(),
            "type": self.object_type_dd.selected_option,
            "assets": self.loaded_assets,
        }


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
        param1 = self.first_param.selected_option[0]
        param2 = self.second_param.selected_option[0]

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
        param1 = self.first_param.selected_option[0]
        param2 = self.second_param.selected_option[0]

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
