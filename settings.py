# settings.py
API_VERSION = "v1"
DEBUG = True

# 기본 프로필 사진
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"
DEFAULT_PROFILE_PIC = "https://via.placeholder.com/150"

# 토큰 만료 시간
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Claude API
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
