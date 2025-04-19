import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextBox, UIDropDownMenu


# def update_positions(root):
#     stack = [root]
#     while stack:
#         current = stack.pop()

#         for child in current.child_blocks:

#             child.abs_pos = current.abs_pos + child.local_offset
#             child.set_relative_position(child.abs_pos)
#             stack.append(child)
SNAP_TOLERANCE = 20
all_workspaces = []
blocks = []


class Slot:
    """A docking slot living inside an ActionWorkspace."""

    def __init__(self, rel_pos):
        self.rel_pos = rel_pos  # tuple (x,y) inside the workspace
        self.size = (120, 40)  # same size as block
        self.occupied = None  # points to DraggableBlock or None

    def rect(self):
        return pygame.Rect(self.rel_pos, self.size)


class DraggableBlock(UIButton):
    def __init__(
        self, relative_rect, manager, text, container, param_defs=None, **kwargs
    ):

        # the block *itself* (acts as the drag handle too)
        super().__init__(
            relative_rect=relative_rect,
            text=text,
            manager=manager,
            container=container,
            **kwargs,
        )

        #  create & memorise each param dropdown
        self._param_widgets = []  # list of (offset, widget)
        for label, pos, options in param_defs or []:
            dd = UIDropDownMenu(
                options_list=options,
                starting_option=options[0],
                relative_rect=pygame.Rect(
                    relative_rect.x + pos[0] - 40, relative_rect.y + pos[1] - 10, 50, 30
                ),
                manager=manager,
                container=container,
            )
            offset = pygame.Vector2(pos)  # offset w.r.t. block.topleft
            self._param_widgets.append((offset, dd))

        # ❸ drag state
        self.is_dragging = False
        self._drag_offset = (0, 0)
        self.docked_slot = None
        self.toggled = False

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
            if self.docked_slot:
                self.docked_slot.occupied = None
                self.docked_slot = None

            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self.mouse_down_pos = event.pos
                abs_r = self.get_abs_rect()
                mx, my = event.pos
                self.drag_offset = (abs_r.x - mx, abs_r.y - my)
                return handled

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                self.unfocus()

                # look for a free slot in any workspace
                for ws in all_workspaces:
                    snap = ws.get_snap_slot(self.get_abs_rect())
                    if snap:
                        # dock into it
                        self.docked_slot = snap
                        snap.occupied = self
                        # THIS re‑parents the block into the workspace
                        abs_slot_x = ws.get_abs_rect().x + snap.rel_pos[0]
                        abs_slot_y = ws.get_abs_rect().y + snap.rel_pos[1]

                        # now get this block's container (still center_panel)
                        container_rect = self.ui_container.get_abs_rect()

                        # set rel position inside that panel, calculated from abs position
                        rel_x = abs_slot_x - container_rect.x
                        rel_y = abs_slot_y - container_rect.y

                        self.set_relative_position((rel_x, rel_y))
                        break

                # small‑click still toggles
                dx = abs(event.pos[0] - self.mouse_down_pos[0])
                dy = abs(event.pos[1] - self.mouse_down_pos[1])
                if dx < 5 and dy < 5:
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

    # (optional) tidy‑up when the block is killed
    def kill(self):
        for _, widget in self._param_widgets:
            widget.kill()
        super().kill()


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

        self.slots = []

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

        # ───── CONFIG ─────
        NUM_SLOTS = 8
        SLOT_W, SLOT_H = 120, 40
        MARGIN_X = 20  # px on left & right
        H_SPACING = 10  # horizontal gap
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
        y_pre = self.preconditions_label.get_relative_rect().bottom + V_SPACING
        y_ifx = self.immediateFX_label.get_relative_rect().bottom + V_SPACING
        y_sfx = self.specialFX_label.get_relative_rect().bottom + V_SPACING

        # build wrapped rows for each section
        for base_y in (y_pre, y_ifx, y_sfx):
            for i in range(NUM_SLOTS):
                row, col = divmod(i, slots_per_row)
                x = MARGIN_X + col * (SLOT_W + spacing_x)
                y = base_y + row * (SLOT_H + V_SPACING)
                self.slots.append(Slot((x, y)))

    # def draw_debug_slots(self, surf):
    #     for slot in self.slots:
    #         abs_x = self.get_abs_rect().x + slot.rel_pos[0]
    #         abs_y = self.get_abs_rect().y + slot.rel_pos[1]
    #         pygame.draw.rect(
    #             surf,
    #             (
    #                 pygame.Color("gray")
    #                 if slot.occupied is None
    #                 else pygame.Color("darkgreen")
    #             ),
    #             pygame.Rect((abs_x, abs_y), slot.size),
    #             2,
    #         )

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

    def attach_block(self, block):
        self.attached_blocks.append(block)
