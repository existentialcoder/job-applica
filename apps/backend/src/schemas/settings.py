import enum
from typing import Any

from pydantic import BaseModel


class UserTheme(enum.StrEnum):
    LIGHT = 'light'
    DARK = 'dark'
    SYSTEM = 'system'


class ViewMode(enum.StrEnum):
    BOARD = 'board'
    LIST = 'list'


class DarkBgTheme(enum.StrEnum):
    NOIR = 'noir'
    MOCHA = 'mocha'
    ABYSS = 'abyss'
    MIDNIGHT = 'midnight'


class LightBgTheme(enum.StrEnum):
    WHITE = 'white'
    CANVAS = 'canvas'
    ARCTIC = 'arctic'
    BLUSH = 'blush'


class UserSettings(BaseModel):
    theme: UserTheme = UserTheme.SYSTEM
    view_mode: ViewMode = ViewMode.LIST
    per_page: int = 10
    dark_bg_theme: DarkBgTheme = DarkBgTheme.NOIR
    light_bg_theme: LightBgTheme = LightBgTheme.WHITE
    sidebar_expanded: bool = True
    hidden_widgets: list[str] = []
    saved_job_filters: dict[str, Any] | None = None
