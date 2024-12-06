import pygame
import pygame_gui

from frontend.constants import MAIN_MENU
from frontend.screen import ScreenInterface
from pygame_gui.elements import UIPanel, UISelectionList

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

        self.selected_item = None
        self.grid_items = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Initialize pygame_gui manager
        self.ui_manager = pygame_gui.UIManager(window_size)

        # Sidebar Panel
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(self.screen_width - 220, 0, 220, self.screen_height),
            manager=self.ui_manager,
        )

        # Sidebar Tabs
        self.sidebar_tabs = UISelectionList(
            relative_rect=pygame.Rect(10, 10, 200, 150),
            item_list=["Items", "Container", "Station", "Other"],
            manager=self.ui_manager,
            parent_element=self.sidebar_panel,
        )

        # Item List
        self.item_list = UISelectionList(
            relative_rect=pygame.Rect(10, 180, 200, 800),
            item_list=["steak", "cabbage", "strawberry"],  # Default items
            manager=self.ui_manager,
            parent_element=self.sidebar_panel,
        )

    def load_assets(self):
        """Load necessary assets."""
        # No additional assets to load here

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

        # Handle tab selection
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.sidebar_tabs:
                selected_tab = event.text
                if selected_tab == "Items":
                    self.item_list.set_item_list(["steak", "cabbage", "strawberry"])
                elif selected_tab == "Container":
                    self.item_list.set_item_list(["plate", "tray"])
                elif selected_tab == "Station":
                    self.item_list.set_item_list(["grill", "oven"])
                elif selected_tab == "Other":
                    self.item_list.set_item_list(["decor"])
            elif event.ui_element == self.item_list:
                self.selected_item = event.text

        # Handle grid interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                x, y = event.pos
                grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
                grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    self.grid_items[grid_y][grid_x] = self.selected_item

            elif event.button == 3:  # Right click to remove
                x, y = event.pos
                grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
                grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    self.grid_items[grid_y][grid_x] = None

        elif event.type == pygame.MOUSEWHEEL:
            self.zoom += event.y * 0.1
            self.zoom = max(0.5, min(2.0, self.zoom))  # Clamp zoom level

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
