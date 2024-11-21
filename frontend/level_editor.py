import pygame
from frontend.constants import *
from frontend.image import Image
from frontend.screen import ScreenInterface
from frontend.loading import LoadingScreen

# Set up the assets directory
ASSETS_DIRECTORY = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "matchmaking"))


class LevelEditorScreen(ScreenInterface):
    def __init__(self, window_size):
        """
        Initialize the Lobby Screen.

        Args:
            window_size (tuple): (width, height) of the window
        """
        super().__init__(window_size)
        self.window_size = window_size
        self.grid_width = 20
        self.grid_height = 20
        self.cell_size = 32
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0

        self.selected_item = None
        self.grid_items = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Sidebar elements
        self.sidebar_tabs = ["items", "container", "station", "other"]
        self.active_tab = "items"
        self.sidebar_items = {
            "items": ["steak", "cabbage", "strawberry"],
            "container": ["plate", "tray"],
            "station": ["grill", "oven"],
            "other": ["decor"]
        }
        self.background = Image(self.screen, self.background_image, 0.5, 0.5, self.scale_factor, anchor="center")
        self.host = False
        self.count = 0

    def load_assets(self):
        """Load necessary assets."""
        background_path = os.path.join(SHARED_DIRECTORY, "background.png")
        self.background_image = LoadingScreen.ASSET[background_path]

    def draw(self):
        """Draws all the screen components."""
        self.background.draw()
        self._draw_grid(self.screen)
        self._draw_sidebar(self.screen)

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

    def _draw_sidebar(self, surface):
        """Render the sidebar with item categories and selections in horizontal tab layout, fixing alignment issues."""
        sidebar_width = 200
        sidebar_height = surface.get_height()

        # Draw sidebar background
        pygame.draw.rect(surface, (240, 240, 240),
                         (surface.get_width() - sidebar_width, 0, sidebar_width, sidebar_height))

        font = pygame.font.SysFont(None, 24)

        # Draw horizontal tabs at the top
        tab_width = sidebar_width // len(self.sidebar_tabs)
        tab_height = 40
        tab_rects = []  # Store rects for event handling
        for i, tab in enumerate(self.sidebar_tabs):
            tab_rect = pygame.Rect(surface.get_width() - sidebar_width + i * tab_width, 0, tab_width, tab_height)
            tab_rects.append(tab_rect)  # Save for event handling
            pygame.draw.rect(surface, (200, 200, 200) if self.active_tab == tab else (220, 220, 220), tab_rect)
            pygame.draw.rect(surface, (150, 150, 150), tab_rect, 1)  # Border for the tab
            text = font.render(tab.capitalize(), True, (0, 0, 0))
            text_rect = text.get_rect(center=tab_rect.center)
            surface.blit(text, text_rect)

        # Draw items for the active tab below the horizontal tabs
        items = self.sidebar_items[self.active_tab]
        item_start_y = tab_height + 10  # Start drawing items below the tabs with some padding
        item_rect_height = 50
        item_rects = []  # Store rects for event handling
        for i, item in enumerate(items):
            item_rect = pygame.Rect(
                surface.get_width() - sidebar_width,
                item_start_y + i * (item_rect_height + 5),  # Add 5px padding between items
                sidebar_width,
                item_rect_height
            )
            item_rects.append(item_rect)  # Save for event handling
            pygame.draw.rect(surface, (180, 180, 180) if self.selected_item == item else (220, 220, 220), item_rect)
            pygame.draw.rect(surface, (150, 150, 150), item_rect, 1)  # Border for the item
            text = font.render(item.capitalize(), True, (0, 0, 0))
            text_rect = text.get_rect(center=item_rect.center)
            surface.blit(text, text_rect)

        # Save rects for later event handling
        self.tab_rects = tab_rects
        self.item_rects = item_rects

    def handle_events(self, event):
        """Handle user interactions for the grid and sidebar."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Check if clicking on horizontal tabs
            for i, tab_rect in enumerate(self.tab_rects):
                if tab_rect.collidepoint(x, y):
                    self.active_tab = self.sidebar_tabs[i]
                    return

            # Check if clicking on items in the active tab
            for i, item_rect in enumerate(self.item_rects):
                if item_rect.collidepoint(x, y):
                    items = self.sidebar_items[self.active_tab]
                    self.selected_item = items[i]
                    return

            # Check if clicking on the grid
            grid_x = int((x - self.offset_x) / (self.cell_size * self.zoom))
            grid_y = int((y - self.offset_y) / (self.cell_size * self.zoom))
            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                self.grid_items[grid_y][grid_x] = self.selected_item

        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Dragging for panning
                self.offset_x += event.rel[0]
                self.offset_y += event.rel[1]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:  # Enable zoom mode
                self.zoom += 0.1 if event.mod & pygame.KMOD_SHIFT else -0.1

    def update(self):
        """Update the screen and handle events."""
        super().update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.set_next_screen(MAIN_MENU)
                elif event.key == pygame.K_g:
                    self.set_next_screen(GAME)
            self.handle_events(event)
