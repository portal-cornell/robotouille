import pygame
import pygame_gui

from frontend.constants import MAIN_MENU
from frontend.screen import ScreenInterface
from pygame_gui.elements import UIPanel, UIButton, UISelectionList


class LevelEditorScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Level Editor Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size)
        self.grid_width = 20
        self.grid_height = 20
        self.cell_size = 32
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.is_dragging = False
        self.last_mouse_pos = None

        self.selected_item = "steak"  # Default selected item
        self.selected_button = None  # Track the currently selected button
        self.grid_items = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.item_buttons = []  # Initialize item_buttons as an empty list

        # Initialize pygame_gui manager
        self.ui_manager = pygame_gui.UIManager(window_size)

        # Sidebar Panel - Positioned to the far right
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(self.screen_width - 220, 0, 220, self.screen_height),
            manager=self.ui_manager,
        )

        # Sidebar Tabs with old styling (UISelectionList)
        self.sidebar_tabs = UISelectionList(
            relative_rect=pygame.Rect(10, 10, 200, 150),
            item_list=["Items", "Container", "Station", "Other"],
            manager=self.ui_manager,
            parent_element=self.sidebar_panel,
        )

        # Simulate default tab selection
        self.current_tab = "Items"
        self.update_item_buttons()

    def load_assets(self):
        """Load necessary assets for the screen."""
        pass

    def update_item_buttons(self):
        """Update the item buttons based on the selected tab."""
        # Correctly remove old buttons
        for button, _ in self.item_buttons:
            button.kill()
        self.item_buttons = []

        items = {
            "Items": ["steak", "cabbage", "strawberry"],
            "Container": ["plate", "tray"],
            "Station": ["grill", "oven"],
            "Other": ["decor"],
        }

        item_list = items[self.current_tab]

        for i, item in enumerate(item_list):
            button = UIButton(
                relative_rect=pygame.Rect(10, 180 + i * 50, 200, 40),
                text="",  # No text; purely image-based
                manager=self.ui_manager,
                parent_element=self.sidebar_panel,
                object_id=f"#item_{item}",
            )
            self.item_buttons.append((button, item))  # Store button and its associated item

            # If the button matches the default selected item, set it as active
            if item == self.selected_item:
                self.selected_button = button

        self._update_button_states()  # Ensure button states are updated for the default selection

    def _update_button_states(self):
        """Update the states of item buttons to reflect selection."""
        for button, item in self.item_buttons:
            if item == self.selected_item:
                button.select()  # Mark the button as active
            else:
                button.unselect()  # Mark the button as inactive

    def _draw_grid(self, surface):
        """Render the grid with current offset and zoom."""
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x = col * self.cell_size * self.zoom + self.offset_x
                y = row * self.cell_size * self.zoom + self.offset_y
                pygame.draw.rect(surface, (200, 200, 200),
                                 (x, y, self.cell_size * self.zoom, self.cell_size * self.zoom), 1)

                # Draw placed items
                item = self.grid_items[row][col]
                if item:
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(item, True, (0, 0, 0))
                    surface.blit(text, (x + 5, y + 5))

    def handle_events(self, event):
        """Handle events for grid and UI."""
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.sidebar_tabs:
                self.current_tab = self.sidebar_tabs.get_single_selection()
                self.update_item_buttons()

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for button, item in self.item_buttons:
                if event.ui_element == button:
                    self.selected_item = item
                    self.selected_button = button
                    self._update_button_states()

        # Handle grid interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click for panning or item placement
                x, y = event.pos
                if x < self.screen_width - 220:  # Click outside the sidebar
                    grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
                    grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        self.grid_items[grid_y][grid_x] = self.selected_item
                self.is_dragging = True
                self.last_mouse_pos = event.pos

            elif event.button == 3:  # Right click to remove
                x, y = event.pos
                grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
                grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    self.grid_items[grid_y][grid_x] = None

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dx, dy = event.rel
                self.offset_x += dx
                self.offset_y += dy

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEWHEEL:
            old_zoom = self.zoom
            self.zoom += event.y * 0.1
            self.zoom = max(0.5, min(2.0, self.zoom))

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_grid_x = (mouse_x - self.offset_x) / (self.cell_size * old_zoom)
            mouse_grid_y = (mouse_y - self.offset_y) / (self.cell_size * old_zoom)

            self.offset_x = mouse_x - mouse_grid_x * self.cell_size * self.zoom
            self.offset_y = mouse_y - mouse_grid_y * self.cell_size * self.zoom

    def draw(self):
        """Draw grid and UI components."""
        self.screen.fill((50, 50, 50))  # Clear background
        self._draw_grid(self.screen)
        self.ui_manager.draw_ui(self.screen)

    def update(self):
        """Update the screen and handle events."""
        super().update()
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        self.ui_manager.update(time_delta)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.set_next_screen(MAIN_MENU)
            self.handle_events(event)
