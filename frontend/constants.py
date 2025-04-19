import os 

# Traces the clickable region for buttons, and editable textbox
DEBUG = False

# Maximum number of players in the Game
MAX_PLAYERS = 4

# The RBG values associated with colors used throughout the game
BLUE = (2,120,172)
WHITE = (255, 255, 255)
CYAN = (225, 242, 249)
GREY = (109, 109, 109)
LIGHT_GREY = (169, 169, 169)
BLACK = (0, 0, 0)

# Screen identifiers
MAIN_MENU = 'main_menu'
SETTINGS = 'settings'
GAME = 'game'
ENDGAME = 'end_game'
LOADING = 'loading'
LOGO = 'logo'
MATCHMAKING = 'matchmaking'

SHARED_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "frontend", "shared"))

FONT_PATH = os.path.join(SHARED_DIRECTORY, "hug.ttf")