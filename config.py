# ─────────────────────────────────────────────
#  Story Video Generator — Configuration
# ─────────────────────────────────────────────

# Video dimensions (YouTube Shorts = 1080x1920 vertical)
WIDTH  = 1080
HEIGHT = 1920
FPS    = 30

# ── Voice Settings ────────────────────────────
# Options: en-US-AriaNeural, en-US-GuyNeural,
#          en-GB-SoniaNeural, en-IN-NeerjaNeural
VOICE = "en-US-GuyNeural"

# ── Subtitle Settings ─────────────────────────
WORDS_PER_SUBTITLE = 3        # 2 or 3 words at a time
SUBTITLE_FONT_SIZE = 80       # Big and bold for Reels style
SUBTITLE_COLOR     = (255, 255, 255)   # White
SUBTITLE_HIGHLIGHT = (255, 220, 0)     # Yellow highlight on current word
SUBTITLE_SHADOW    = (0, 0, 0)         # Black shadow
SUBTITLE_Y_POS     = 0.72              # Vertical position (0=top, 1=bottom)

# ── Image Settings ────────────────────────────
# Number of background images to generate for the video
NUM_IMAGES = 4

IMAGE_STYLE = (
    "cinematic movie scene, "
    "dramatic lighting, "
    "hyper realistic, "
    "ultra detailed, "
    "4K, dark atmosphere, "
    "emotional storytelling"
)

# ── Directories ───────────────────────────────
ASSETS_DIR = "assets"
OUTPUT_DIR = "output"
