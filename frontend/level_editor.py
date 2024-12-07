import pygame
import pygame_gui

from frontend.constants import MAIN_MENU
from frontend.screen import ScreenInterface
from pygame_gui.elements import UIPanel, UIButton, UILabel


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
        self.selected_button = None  # Track the currently selected button
        self.grid_items = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Initialize pygame_gui manager
        self.ui_manager = pygame_gui.UIManager(window_size)

        # Sidebar Panel - Wider to fit the UI
        self.sidebar_width = 320
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(window_size[0] - self.sidebar_width, 0, self.sidebar_width, window_size[1]),
            manager=self.ui_manager,
        )

        # Tabs container (horizontal row)
        self.tabs_panel = UIPanel(
            relative_rect=pygame.Rect(10, 10, self.sidebar_width - 20, 50),
            manager=self.ui_manager,
            container=self.sidebar_panel,
        )
        self.tabs = ["Items", "Container", "Station", "Other"]
        self.tab_buttons = self._create_tabs()

        # Current selected tab and its items
        self.current_tab = "Items"
        self.items_panel = None  # Placeholder for item buttons
        self.item_buttons = []  # Keep track of item buttons

        # Load all necessary images
        self.item_images = self.load_item_images()

        self.update_item_buttons()

    def load_assets(self):
        """Load necessary assets for the screen."""
        pass

    def load_item_images(self):
        """Load images for all items."""
        items = {
            "steak": "images/steak.png",
            "cabbage": "images/cabbage.png",
            "strawberry": "images/strawberry.png",
            "cooked steak": "images/cooked_steak.png",
            "watermelon slices": "images/watermelon.png",
            "cooked egg": "images/cooked_egg.png",
            "egg": "images/egg.png",
            "raw egg": "images/raw_egg.png",
            "plate": "images/plate.png",
            "tray": "images/tray.png",
            "grill": "images/grill.png",
            "oven": "images/oven.png",
            "decor": "images/decor.png",
        }

        loaded_images = {}
        for name, path in items.items():
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.smoothscale(image, (60, 60))  # Resize to fit the button
                loaded_images[name] = image
            except pygame.error:
                print(f"Error loading image: {path}")
                loaded_images[name] = None  # Fallback if image is missing
        return loaded_images

    def _sanitize_object_id(self, name):
        """Sanitize object_id to remove spaces and disallowed characters."""
        return name.replace(" ", "_").replace(".", "_")

    def _create_tabs(self):
        """Create tab buttons inside the tabs panel (horizontal layout)."""
        tab_buttons = []
        button_width = 70
        spacing = 10
        for i, tab_name in enumerate(self.tabs):
            button = UIButton(
                relative_rect=pygame.Rect(i * (button_width + spacing), 5, button_width, 40),
                text=tab_name,
                manager=self.ui_manager,
                container=self.tabs_panel,
            )
            tab_buttons.append((button, tab_name))
        return tab_buttons

    def update_item_buttons(self):
        """Update the item buttons for the current tab."""
        # Destroy the old item buttons panel, if it exists
        if self.items_panel is not None:
            self.items_panel.kill()

        # Create a new panel to hold item buttons below the tabs
        self.items_panel = UIPanel(
            relative_rect=pygame.Rect(10, 70, self.sidebar_width - 20, 400),
            manager=self.ui_manager,
            container=self.sidebar_panel,
        )
        self.item_buttons = []

        # Items based on the current tab
        items = {
            "Items": [
                {"name": "steak"},
                {"name": "cabbage"},
                {"name": "strawberry"},
                {"name": "cooked steak"},
                {"name": "watermelon slices"},
                {"name": "cooked egg"},
                {"name": "egg"},
                {"name": "raw egg"},
            ],
            "Container": [
                {"name": "plate"},
                {"name": "tray"},
            ],
            "Station": [
                {"name": "grill"},
                {"name": "oven"},
            ],
            "Other": [
                {"name": "decor"},
            ],
        }
        item_list = items.get(self.current_tab, [])

        # Create buttons for the items (arranged in a grid format)
        button_width, button_height = 90, 110  # Adjust height for image + caption
        columns = 3  # Number of buttons per row
        spacing = 10

        for i, item in enumerate(item_list):
            row = i // columns
            col = i % columns

            # Create a UIPanel as a container for the button
            button_panel = UIPanel(
                relative_rect=pygame.Rect(
                    col * (button_width + spacing), row * (button_height + spacing), button_width, button_height
                ),
                manager=self.ui_manager,
                container=self.items_panel,
            )

            # Create a single UIButton for the image and caption
            button = UIButton(
                relative_rect=pygame.Rect(0, 0, button_width, button_height),
                text="",  # Button text left blank for manual caption placement
                manager=self.ui_manager,
                container=button_panel,
                object_id=f"#{self._sanitize_object_id(item['name'])}_button",
            )

            # Render the image onto the button
            image = self.item_images.get(item["name"])
            if image:
                button_panel.drawable_shape.surface.blit(image, (15, 10))

            # Caption below the image
            UILabel(
                relative_rect=pygame.Rect(0, 80, button_width, 20),  # Caption position
                text=item["name"],
                manager=self.ui_manager,
                container=button_panel,
            )

            # Add the button to the list
            self.item_buttons.append((button, item["name"]))

    def _highlight_selected_button(self):
        """Highlight the currently selected button."""
        for button, item in self.item_buttons:
            if self.selected_item == item:
                button.select()  # Mark the selected button
            else:
                button.unselect()  # Unmark all other buttons

    def handle_events(self, event):
        """Handle events for UI and grid interactions."""
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Handle tab selection
            for button, tab_name in self.tab_buttons:
                if event.ui_element == button:
                    self.current_tab = tab_name
                    self.update_item_buttons()

            # Handle item button selection
            for button, item in self.item_buttons:
                if event.ui_element == button:
                    self.selected_item = item
                    self.selected_button = button
                    self._highlight_selected_button()  # Ensure visual feedback

        # Handle grid interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click for panning or item placement
                x, y = event.pos
                if x < self.screen_width - self.sidebar_width:  # Ignore clicks in the sidebar
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
