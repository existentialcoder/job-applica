BG_THEMES = {
    'light': {
        'white': {'bg': '#ffffff', 'card': '#ffffff', 'accent': '#7c3aed', 'accent_fg': '#f9fafb'},
        'canvas': {'bg': '#fcf8f3', 'card': '#fdfcfa', 'accent': '#5b3c10', 'accent_fg': '#f9fafb'},
        'arctic': {'bg': '#f3f7fc', 'card': '#fafbfd', 'accent': '#1a3a6b', 'accent_fg': '#f9fafb'},
        'blush': {'bg': '#fcf3f5', 'card': '#fdfafa', 'accent': '#7a1a2f', 'accent_fg': '#f9fafb'},
    },
    'dark': {
        'noir': {'bg': '#030712', 'card': '#030712', 'accent': '#6d28d9', 'accent_fg': '#f9fafb'},
        'mocha': {'bg': '#120f0d', 'card': '#171412', 'accent': '#d3a969', 'accent_fg': '#0c0a09'},
        'abyss': {'bg': '#070c12', 'card': '#0b1118', 'accent': '#7bafe0', 'accent_fg': '#070c12'},
        'midnight': {'bg': '#0c0811', 'card': '#110d17', 'accent': '#b696e9', 'accent_fg': '#0c0811'},
    },
}

TEXT_COLORS = {
    'light': {'fg': '#030712', 'muted': '#6b7280'},
    'dark': {'fg': '#f9fafb', 'muted': '#9ca3af'},
}

DEFAULT_LIGHT_KEY = 'white'
DEFAULT_DARK_KEY = 'noir'


def resolve_email_theme(user_settings: dict) -> dict:
    """ Resolves a user's persisted theme/settings into email-safe colors. """
    mode = user_settings.get('theme')
    light_key = user_settings.get('light_bg_theme', DEFAULT_LIGHT_KEY)
    dark_key = user_settings.get('dark_bg_theme', DEFAULT_DARK_KEY)

    light = {**BG_THEMES['light'].get(light_key, BG_THEMES['light'][DEFAULT_LIGHT_KEY]), **TEXT_COLORS['light']}
    dark = {**BG_THEMES['dark'].get(dark_key, BG_THEMES['dark'][DEFAULT_DARK_KEY]), **TEXT_COLORS['dark']}

    if mode == 'dark':
        return {'base': dark, 'dark_override': None}
    if mode == 'light':
        return {'base': light, 'dark_override': None}
    return {'base': light, 'dark_override': dark}
