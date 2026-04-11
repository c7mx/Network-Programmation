import os


ROWS = 120
COLS = 120
CELL_SIZE = 40
FPS = 60
BANNER_HEIGHT = 100
EPSILON = 1e-1
HEADLESS_SPEEDUP = 30
ELEVATION_ZONE_PLAT_SIZE = 40
ELEVATON_MAX_VALUE = 16
ELEVATON_MIN_VALUE = 0
K_ELEVATION_H = 1.25
K_ELEVATION_D = 0.75
VIEW_ELEVATION = True
UNIT_RADIUS = 0.3


RED = (255, 60, 60)
BLUE = (60, 60, 255)
GREEN = (0, 128, 0)
YELLOW = (255,255,0)
DARK = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GOLD = (210, 180, 60)
DARK_GRAY = (50, 50, 50)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 120)


# BattleTournament' Scenarios
DEFAULT_SCENARIOS = [
    {"Crossbowman":20, "Pikeman":0,"Knight":0,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10},
    {"Crossbowman":0, "Pikeman":20,"Knight":0,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10},
    {"Crossbowman":0, "Pikeman":0,"Knight":20,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10},
    
    {"Crossbowman":20, "Pikeman":20,"Knight":0,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10},
    {"Crossbowman":0, "Pikeman":20,"Knight":20,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10},
    {"Crossbowman":20, "Pikeman":0,"Knight":20,"startLine":50,"startCol":40,"armyDistance":10,"unitPerCol":10}, 
   
    {"Crossbowman":60, "Pikeman":20,"Knight":20,"startLine":50,"startCol":50,"armyDistance":40,"unitPerCol":10},
    
    {"Crossbowman":60, "Pikeman":60,"Knight":60,"startLine":40,"startCol":40,"armyDistance":15,"unitPerCol":20},
    
    {"Crossbowman":100, "Pikeman":100,"Knight":100,"startLine":40,"startCol":20,"armyDistance":20,"unitPerCol":30}
]


ELEVATION_JSON_FILEPATH = "Elevation.json"
STATS_FILEPATH = "Stats_Units.csv"
STATS_BONUS_FILEPATH = "model/Stats_Bonus.csv"


# Base Picture Path
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

IMAGE_FILES = {
    "Knight_1": {
        "up": "../../img/Sprites/Knight/Red/up.png",
        "down": "../../img/Sprites/Knight/Red/down.png",
        "left": "../../img/Sprites/Knight/Red/left.png",
        "right": "../../img/Sprites/Knight/Red/right.png"
    },
    "Knight_2": {
        "up": "../../img/Sprites/Knight/Blue/up.png",
        "down": "../../img/Sprites/Knight/Blue/down.png",
        "left": "../../img/Sprites/Knight/Blue/left.png",
        "right": "../../img/Sprites/Knight/Blue/right.png"
    },
    "Knight_3": {
        "up": "../../img/Sprites/Knight/Green/up.png",
        "down": "../../img/Sprites/Knight/Green/down.png",
        "left": "../../img/Sprites/Knight/Green/left.png",
        "right": "../../img/Sprites/Knight/Green/right.png"
    },
    "Knight_4": {
        "up": "../../img/Sprites/Knight/Yellow/up.png",
        "down": "../../img/Sprites/Knight/Yellow/down.png",
        "left": "../../img/Sprites/Knight/Yellow/left.png",
        "right": "../../img/Sprites/Knight/Yellow/right.png"
    },

    "Pikeman_1": {
        "up": "../../img/Sprites/Pikeman/Red/up.png",
        "down": "../../img/Sprites/Pikeman/Red/down.png",
        "left": "../../img/Sprites/Pikeman/Red/left.png",
        "right": "../../img/Sprites/Pikeman/Red/right.png"
    },
    "Pikeman_2": {
        "up": "../../img/Sprites/Pikeman/Blue/up.png",
        "down": "../../img/Sprites/Pikeman/Blue/down.png",
        "left": "../../img/Sprites/Pikeman/Blue/left.png",
        "right": "../../img/Sprites/Pikeman/Blue/right.png"
    },
    "Pikeman_3": {
        "up": "../../img/Sprites/Pikeman/Green/up.png",
        "down": "../../img/Sprites/Pikeman/Green/down.png",
        "left": "../../img/Sprites/Pikeman/Green/left.png",
        "right": "../../img/Sprites/Pikeman/Green/right.png"
    },
    "Pikeman_4": {
        "up": "../../img/Sprites/Pikeman/Yellow/up.png",
        "down": "../../img/Sprites/Pikeman/Yellow/down.png",
        "left": "../../img/Sprites/Pikeman/Yellow/left.png",
        "right": "../../img/Sprites/Pikeman/Yellow/right.png"
    },

    "Crossbowman_1": {
        "up": "../../img/Sprites/Crossbowman/Red/up.png",
        "down": "../../img/Sprites/Crossbowman/Red/down.png",
        "left": "../../img/Sprites/Crossbowman/Red/left.png",
        "right": "../../img/Sprites/Crossbowman/Red/right.png"
    },
    "Crossbowman_2": {
        "up": "../../img/Sprites/Crossbowman/Blue/up.png",
        "down": "../../img/Sprites/Crossbowman/Blue/down.png",
        "left": "../../img/Sprites/Crossbowman/Blue/left.png",
        "right": "../../img/Sprites/Crossbowman/Blue/right.png"
    },
    "Crossbowman_3": {
        "up": "../../img/Sprites/Crossbowman/Green/up.png",
        "down": "../../img/Sprites/Crossbowman/Green/down.png",
        "left": "../../img/Sprites/Crossbowman/Green/left.png",
        "right": "../../img/Sprites/Crossbowman/Green/right.png"
    },
    "Crossbowman_4": {
        "up": "../../img/Sprites/Crossbowman/Yellow/up.png",
        "down": "../../img/Sprites/Crossbowman/Yellow/down.png",
        "left": "../../img/Sprites/Crossbowman/Yellow/left.png",
        "right": "../../img/Sprites/Crossbowman/Yellow/right.png"
    }
}


BACKGROUND = "../../img/backgrounds/back.png"
SAVE_FOLDER = "../save/"
LOGS_FOLDER = "../save/logs/"
REPORTS_FOLDER = "../save/reports/"
