import pygame
import pygame_gui

from frontend.constants import MAIN_MENU
from frontend.screen import ScreenInterface
from pygame_gui.elements import UIPanel, UILabel, UIImage


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
        self.tabs = ["Items", "Container", "Station", "Other"]
        self.tab_buttons = self._create_tabs()

        # Current tab and items panel
        self.current_tab = "Items"
        self.items_panel = None
        self.item_panels = []

        # Map items to a common test image for now
        self.item_image_map = self.load_item_image_map()

        self.update_item_buttons()

    def load_assets(self):
        """Load necessary assets for the screen."""
        pass

    def load_item_image_map(self):
        """Map all items to the same test image."""
        items = [
            "steak", "cabbage", "strawberry", "cooked steak", "watermelon slices",
            "cooked egg", "egg", "raw egg", "plate", "tray", "grill", "oven", "decor"
        ]
        try:
            test_image = pygame.image.load("assets/tomato.png").convert_alpha()
            test_image = pygame.transform.smoothscale(test_image, (60, 60))  # Resize for buttons
        except pygame.error:
            print("Error loading test image: assets/tomato.png")
            test_image = None  # Fallback if the image is missing

        # Map all items to the same test image
        return {item: test_image for item in items}

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
        self.item_panels = []

        # Items based on the current tab
        items = {
            "Items": ["steak", "cabbage", "strawberry", "cooked steak", "watermelon slices"],
            "Container": ["plate", "tray"],
            "Station": ["grill", "oven"],
            "Other": ["decor"],
        }
        item_list = items.get(self.current_tab, [])

        # Create a grid of buttons with images and captions
        button_width, button_height = 90, 110
        columns = 3
        spacing = 10

        for i, item_name in enumerate(item_list):
            row = i // columns
            col = i % columns

            # Panel for each item
            item_panel = UIPanel(
                relative_rect=pygame.Rect(
                    col * (button_width + spacing),
                    row * (button_height + spacing),
                    button_width,
                    button_height,
                ),
                manager=self.ui_manager,
                container=self.items_panel,
            )

            # Image for the item
            image_surface = self.item_image_map.get(item_name)
            if image_surface:
                UIImage(
                    relative_rect=pygame.Rect(15, 10, 60, 60),  # Position image in the center
                    image_surface=image_surface,
                    manager=self.ui_manager,
                    container=item_panel,
                )

            # Caption for the item
            UILabel(
                relative_rect=pygame.Rect(0, 80, button_width, 20),  # Position below the image
                text=item_name,
                manager=self.ui_manager,
                container=item_panel,
            )

            # Store the panel for further interaction
            self.item_panels.append((item_panel, item_name))

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
            for panel, item_name in self.item_panels:
                if event.ui_element == panel:
                    self.selected_item = item_name

        # Handle grid panning
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_dragging = True
                self.last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            dx, dy = event.rel
            self.offset_x += dx
            self.offset_y += dy

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

    def _draw_grid(self, surface):
        """Render the grid."""
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
