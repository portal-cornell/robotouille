import pygame
import pygame_gui
from pygame_gui.elements import UIPanel

pygame.init()
pygame.display.set_caption('Level Editor')

# game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LOWER_MARGIN = 300
SIDE_MARGIN = 300

window_surface = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))

# game variables
ROWS = 12
MAX_COLUMNS = 16
TILE_SIZE = SCREEN_HEIGHT // ROWS
selected_item = 0

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (144, 201, 120)
BEIGE = pygame.Color('#EDE8D0')

# load tile images
TAB1_TYPES = 8
img_list = []
for x in range(TAB1_TYPES):
    img = pygame.image.load(f'{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# print(img_list)
img_list1 = img_list[:3]
# print(img_list1)
img_list2 = img_list[3:6]
# print(img_list2)
img_list3 = img_list[6:]
# print(img_list3)

background = pygame.Surface((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
background.fill(BEIGE)
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN), theme_path="button.json")
manager.set_visual_debug_mode(True)

is_running = True

# create empty tile list
grid_data = []
for i in range(ROWS):
    r = [-1] * MAX_COLUMNS
    grid_data.append(r)

# draw grid
def draw_grid():
    # vertical lines
    for col in range(MAX_COLUMNS + 1):
        pygame.draw.line(background, WHITE, (col * TILE_SIZE, 0), (col * TILE_SIZE, SCREEN_HEIGHT))
    # horizontal lines
    for row in range(ROWS + 1):
        pygame.draw.line(background, WHITE, (0, row * TILE_SIZE), (SCREEN_WIDTH, row * TILE_SIZE))

# draw items on grid
def draw_items_grid():
    for y_coord, row in enumerate(grid_data):
        for x_coord, tile in enumerate(row):
            if tile >= 0:
                font = pygame.font.SysFont(None, 24)
                text = font.render("" + str(tile), True, (0, 0, 0))
                background.blit(text, (x_coord * TILE_SIZE + 10, y_coord * TILE_SIZE + 15))

# button list
button_list = []
button_list1 = []
button_list2 = []
button_list3 = []
caption_list = []
caption_list1 = []
caption_list2 = []
caption_list3 = []
button_col = 0
button_row = 0

side_panel = UIPanel(relative_rect=pygame.Rect(SCREEN_WIDTH, 0, SIDE_MARGIN + 200, SCREEN_HEIGHT), manager=manager)

# item buttons
for i in range(8):
    tile_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 100), (50, 50)), text='item' + str(i + 1), manager=manager,)
    # caption_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(((75 * button_col) + 40, 75 * button_row + 150), (75, 25)), text='item' + str(i + 1), manager=manager, container=side_panel)
    button_list.append(tile_button)
    # caption_list.append(caption_list1)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

# layering text
layer_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, SCREEN_HEIGHT), (100, 50)), text='Layers', manager=manager)

# button tabs
layer_list = []
for i in range(3):
    layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, SCREEN_HEIGHT + 75 * i + 50), (100, 50)), text='type' + str(i + 1), manager=manager)
    layer_list.append(layer_button)


selected_tab = 0
while is_running:
    time_delta = clock.tick(60) / 1000.0
    draw_grid()
    draw_items_grid()
    # draw tile panel and tiles
    pygame.draw.rect(background, BLACK, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(layer_list, selected_tab)
            if side_panel is not None:
                side_panel.kill()
            for i in range(len(button_list)):
                if event.ui_element == button_list[i]:
                    selected_item = i + 1
                    print(f"Selected: item {selected_item}")
            for i in range(len(layer_list)):
                if event.ui_element == layer_list[i]:
                    selected_tab = i + 1
                    print(f"Selected: type {selected_tab}")
                    tab_label = pygame_gui.elements.UILabel(
                        relative_rect=pygame.Rect((40, 50), (75, 25)),
                        text='type' + str(selected_tab), manager=manager, container=side_panel)
                    button_col = 0
                    button_row = 0
                    start = 0
                    end = 0
                    # have preexisting lists
                    if selected_tab == 1:
                        end = 3
                    elif selected_tab == 2:
                        start = 3
                        end = 6

                    else:
                        start = 6
                        end = 8
                    for i in range(len(button_list)):
                        button_list[i].hide()
                    for i in range(start, end):
                        print(i)
                        print("showing")
                        button_list[i].show()


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x,y = event.pos
                if x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                    print("Clicked outside grid")
                else:
                    x = x // TILE_SIZE
                    y = y // TILE_SIZE
                    grid_data[y][x] = selected_item
                    print(f"Placed: item {selected_item} at ({x}, {y})")


        manager.process_events(event)
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)
    pygame.display.update()



