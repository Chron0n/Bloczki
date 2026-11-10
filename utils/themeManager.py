from dataclasses import dataclass

@dataclass
class ColorTheme:
    menu_bg: tuple[int, int, int]
    menu_button: tuple[int, int, int]
    menu_text: tuple[int, int, int]

    game_bg: tuple[int, int, int]
    frame_selected: tuple[int, int, int]
    frame_notselected: tuple[int, int, int]

    pause_bg: tuple[int, int, int]
    pause_button: tuple[int, int, int]
    pause_text: tuple[int, int, int]

    alpha: int

    neutral_white: tuple[int, int, int]
    neutral_black: tuple[int, int, int]

LIGHT_MODE = ColorTheme(
    menu_bg=(55, 187, 191),
    menu_button=(116, 149, 150),
    menu_text=(28, 31, 31),

    game_bg=(232, 228, 245),
    frame_selected=(12, 242, 164),
    frame_notselected=(13, 189, 129),

    pause_bg=(55, 187, 191),
    pause_button=(116, 149, 150),
    pause_text=(28, 31, 31),

    alpha=220,

    neutral_white=(255, 255, 255),
    neutral_black=(0, 0, 0)
)

DARK_MODE = ColorTheme(
    menu_bg=(25, 127, 130),
    menu_button=(56, 71, 71),
    menu_text=(225, 235, 235),

    game_bg=(40, 40, 40),
    frame_selected=(12, 242, 164),
    frame_notselected=(13, 189, 129),

    pause_bg=(25, 127, 130),
    pause_button=(56, 71, 71),
    pause_text=(225, 235, 235),

    alpha=220,

    neutral_white=(255, 255, 255),
    neutral_black=(0, 0, 0)
)

activeTheme = DARK_MODE

def toggle_dark_mode():
    global activeTheme
    if activeTheme == LIGHT_MODE:
        activeTheme = DARK_MODE
    else:
        activeTheme = LIGHT_MODE