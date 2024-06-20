import json
from typing import TypeAlias, Iterable, Literal


Color: TypeAlias = str|Iterable[int]

SETTINGS = json.load(open("settings.json"))

TILE_SIZE: int = SETTINGS["tile-size"]

TILES_IN_WIDTH  = SETTINGS["width-in-tiles" ]
TILES_IN_HEIGHT = SETTINGS["height-in-tiles"]
WIDTH : int = TILES_IN_WIDTH  * TILE_SIZE
HEIGHT: int = TILES_IN_HEIGHT * TILE_SIZE

TFPS: int = SETTINGS["target-fps"]

BG_COLOR: Color = SETTINGS["bg-color"]
LINES_COLOR: Color = SETTINGS["lines-color"]
LINES_WIDTH: int = SETTINGS["lines-width"]
HALF_LINE_WIDTH = LINES_WIDTH // 2
TILE_SIZE_IN_LINES = TILE_SIZE - LINES_WIDTH

SNAKE_START_SIZE: int = SETTINGS["snake"]["snake-start-size"]

FOOD_COLOR: Color = SETTINGS["food-color"]
SNAKE_COLORS: list[Color] = SETTINGS["snake"]["snake-colors"]

SNAKE_COLORS_LEN = len(SNAKE_COLORS)
SNAKE_COLORS_LEN_M1 = SNAKE_COLORS_LEN - 1

FRAME_BREAKER: int = SETTINGS["frame-breaker"]

TRANSPARENT_SNAKE_TAIL: bool = SETTINGS["snake"]["transparent-tail"]

SPEED: float = SETTINGS["step-in-seconds"]

ICON_PATH: str = SETTINGS["icon-path"]
FONT_PATH: str = SETTINGS["font-path"]
TEXTURE_PATH: str = SETTINGS["textures-path"]
RENDER_TEXTURES: bool = SETTINGS["snake"]["render-textures"]

PRIMARY_COL: Color = SETTINGS["snake"]["primary-color"]
SECONDARY_COL: Color = SETTINGS["snake"]["secondary-color"]
TONGUE_COL: Color = SETTINGS["snake"]["tongue-color"]

WHITE: Color = SETTINGS["snake"]["white"]
BLACK: Color = SETTINGS["snake"]["black"]
RED  : Color = SETTINGS["snake"]["red"  ]