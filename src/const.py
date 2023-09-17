from enum import Enum, auto

FPS = 60

WIDTH, HEIGHT = 800, 800
NUM_COL, NUM_ROW = 25, 25
VER_WIDTH, VER_HEIGHT = WIDTH//NUM_COL, HEIGHT//NUM_ROW

BLACK = (255, 255, 255)
PAS_GREEN = (196, 238, 221)
GRAY = (105, 100, 100)
RED = (204, 39, 11)
LBLUE = (184, 203, 239)
DBLUE = (38, 148, 232)
GREEN = (10, 200, 30)
PURPULE = (128, 0, 128)
ORANGE = (255, 165, 0)

class Mode(Enum):
    OBSTACLE = auto()
    PATH = auto()
    SIMULATION = auto()
    PRE_SIM = auto()
    RECONSTRUCT = auto()
    IDLE = auto()
    MAKE_STEP = auto()