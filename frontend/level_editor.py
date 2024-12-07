import json
import os

import pygame
import pygame_gui

from frontend.constants import MAIN_MENU
from frontend.screen import ScreenInterface
from pygame_gui.elements import UIPanel, UIButton, UIImage, UILabel


class LevelEditorScreen(ScreenInterface):
    def load_assets(self):
        pass

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

        self.selected_item = None  # No default selected item
        self.grid_items = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Initialize pygame_gui manager
        self.ui_manager = pygame_gui.UIManager(window_size)

        # Sidebar Panel - Positioned to the right
        self.sidebar_width = 320
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(window_size[0] - self.sidebar_width, 0, self.sidebar_width, window_size[1]),
            manager=self.ui_manager,
        )

        # Tabs for switching item categories
        self.tabs = ["Item", "Station", "Container"]
        self.tab_buttons = self._create_tabs()

        # Current tab and items panel
        self.current_tab = "Item"
        self.items_panel = None
        self.item_buttons = []  # Interactive buttons

        # Load item data and images
        self.data = self.load_data_from_json("robotouille_config.json")
        self.item_image_map = self.load_item_images()

        self.update_item_buttons()

    def load_data_from_json(self, filepath):
        """Load entity data from the given JSON file."""
        CONFIG_DIR = os.path.join(os.path.dirname(__file__))
        with open(os.path.join(CONFIG_DIR, "..", "renderer", "configuration", filepath), "r") as file:
            data = json.load(file)

        # Extract entities by category
        entities = {
            "Item": data.get("item", {}).get("entities", {}),
            "Station": data.get("station", {}).get("entities", {}),
            "Container": data.get("container", {}).get("entities", {}),
        }
        return entities

    def _draw_grid(self, surface):
        """Render the grid."""
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # Calculate cell position based on zoom and offsets
                x = col * self.cell_size * self.zoom + self.offset_x
                y = row * self.cell_size * self.zoom + self.offset_y

                # Draw the grid cell as a rectangle
                pygame.draw.rect(surface, (200, 200, 200),
                                 (x, y, self.cell_size * self.zoom, self.cell_size * self.zoom), 1)

                # Draw the items in the grid
                item = self.grid_items[row][col]
                if item:
                    # Render the item's text or image
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(item, True, (0, 0, 0))
                    surface.blit(text, (x + 5, y + 5))

    def load_item_images(self):
        """Map each entity to its `default` image."""
        image_map = {}
        for category, entities in self.data.items():
            for name, details in entities.items():
                asset_path = details.get("assets", {}).get("default")
                try:
                    if asset_path:
                        image = pygame.image.load(f"assets/{asset_path}").convert_alpha()
                        image = pygame.transform.smoothscale(image, (60, 60))
                    else:
                        image = None
                except pygame.error:
                    image = None  # Fallback if image is missing
                image_map[name] = image
        return image_map

    def _create_tabs(self):
        """Create horizontal tabs for switching categories."""
        button_width = 70
        spacing = 10
        tab_buttons = []

        for i, tab_name in enumerate(self.tabs):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    10 + i * (button_width + spacing), 10, button_width, 30
                ),
                text=tab_name,
                manager=self.ui_manager,
                container=self.sidebar_panel,
            )
            tab_buttons.append((button, tab_name))
        return tab_buttons

    def update_item_buttons(self):
        """Update the item buttons displayed in the items panel."""
        # Clear previous items panel
        if self.items_panel:
            self.items_panel.kill()

        # Create a new panel for items
        self.items_panel = UIPanel(
            relative_rect=pygame.Rect(10, 50, self.sidebar_width - 20, 500),
            manager=self.ui_manager,
            container=self.sidebar_panel,
        )
        self.item_buttons = []

        # Items based on the current tab
        entities = self.data.get(self.current_tab, {})

        # Create a grid of buttons with images and captions
        button_width, button_height = 90, 110
        columns = 3
        spacing = 10

        for i, (item_name, details) in enumerate(entities.items()):
            row = i // columns
            col = i % columns

            # Button for interactivity
            button = UIButton(
                relative_rect=pygame.Rect(
                    col * (button_width + spacing),
                    row * (button_height + spacing),
                    button_width,
                    button_height,
                ),
                text="",  # No text for button
                manager=self.ui_manager,
                container=self.items_panel,
                object_id=f"#button_{item_name.replace(' ', '_')}",
            )

            # Overlay image above the button
            image_surface = self.item_image_map.get(item_name)
            if image_surface:
                UIImage(
                    relative_rect=pygame.Rect(
                        col * (button_width + spacing) + 15,
                        row * (button_height + spacing) + 10,
                        60,
                        60,
                    ),
                    image_surface=image_surface,
                    manager=self.ui_manager,
                    container=self.items_panel,
                )

            # Overlay caption below the image
            UILabel(
                relative_rect=pygame.Rect(
                    col * (button_width + spacing),
                    row * (button_height + spacing) + 80,
                    button_width,
                    20,
                ),
                text=item_name,
                manager=self.ui_manager,
                container=self.items_panel,
            )

            self.item_buttons.append((button, item_name))

    def handle_events(self, event):
        """Handle events for UI and interactions."""
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Handle tab changes
            for button, tab_name in self.tab_buttons:
                if event.ui_element == button:
                    self.current_tab = tab_name
                    self.update_item_buttons()

            # Handle item selection
            for button, item_name in self.item_buttons:
                if event.ui_element == button:
                    self.selected_item = item_name
                    print(f"Selected item: {self.selected_item}")

        # Handle grid interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click for placing item
                x, y = event.pos
                if x < self.sidebar_width:
                    print("Clicked inside sidebar, ignoring")
                    return
                grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
                grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    self.grid_items[grid_y][grid_x] = self.selected_item
                    print(f"Placed {self.selected_item} at ({grid_x}, {grid_y})")

                self.is_dragging = True
                self.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx, dy = event.rel
            self.offset_x += dx
            self.offset_y += dy

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

    def draw(self):
        """Draw the grid and UI."""
        self.screen.fill((50, 50, 50))  # Clear the background
        self._draw_grid(self.screen)
        self.ui_manager.draw_ui(self.screen)

    def update(self):
        """Update the UI and handle events."""
        super().update()
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        self.ui_manager.update(time_delta)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.set_next_screen(MAIN_MENU)
            self.handle_events(event)
