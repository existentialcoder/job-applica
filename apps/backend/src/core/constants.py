class Constants:
    API_V1_PREFIX = '/api/v1'
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    AUTH_ALGORITHM: str = 'HS256'
    LOGO_URL_TEMPLATE: str = 'https://icons.duckduckgo.com/ip3/{domain}.ico'
    EMAIL_REGEX: str = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    RESET_TOKEN_EXPIRE_MINUTES: int = 5
    OTP_EXPIRE_MINUTES: int = 2
