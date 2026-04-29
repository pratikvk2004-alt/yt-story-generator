import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import VideoClip, AudioFileClip
from config import (
    WIDTH, HEIGHT, FPS, OUTPUT_DIR,
    WORDS_PER_SUBTITLE, SUBTITLE_FONT_SIZE,
    SUBTITLE_COLOR, SUBTITLE_SHADOW, SUBTITLE_Y_POS
)


# ─────────────────────────────────────────────
#  Font Loader
# ─────────────────────────────────────────────

def _get_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/verdanab.ttf" if bold else "C:/Windows/Fonts/verdana.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ─────────────────────────────────────────────
#  Subtitle Grouping
# ─────────────────────────────────────────────

def group_words_into_subtitles(word_timings, words_per_group=3):
    """
    Group word timings into subtitle chunks.
    Returns list of: {"text": str, "start": float, "end": float}
    """
    groups = []
    i = 0
    while i < len(word_timings):
        chunk = word_timings[i : i + words_per_group]
        text  = " ".join(w["word"] for w in chunk)
        start = chunk[0]["start"]
        end   = chunk[-1]["start"] + chunk[-1]["duration"]
        groups.append({"text": text, "start": start, "end": end})
        i += words_per_group
    return groups


# ─────────────────────────────────────────────
#  Frame Renderer
# ─────────────────────────────────────────────

def _draw_subtitle_on_frame(pil_img, subtitle_text):
    """
    Draw Reels-style bold centered subtitle on a PIL image.
    Returns modified PIL image.
    """
    img = pil_img.copy()
    draw = ImageDraw.Draw(img)
    font = _get_font(SUBTITLE_FONT_SIZE, bold=True)

    # Wrap long subtitles
    words = subtitle_text.split()
    lines = []
    current_line = []
    max_width = WIDTH - 100

    for word in words:
        current_line.append(word)
        test = " ".join(current_line)
        try:
            bbox = draw.textbbox((0, 0), test, font=font)
            w = bbox[2] - bbox[0]
        except Exception:
            w = len(test) * (SUBTITLE_FONT_SIZE // 2)
        if w > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(test)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))

    # Calculate position
    line_h = SUBTITLE_FONT_SIZE + 20
    total_h = len(lines) * line_h
    y = int(HEIGHT * SUBTITLE_Y_POS) - total_h // 2

    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
        except Exception:
            text_w = len(line) * (SUBTITLE_FONT_SIZE // 2)

        x = (WIDTH - text_w) // 2

        # Draw thick shadow (multiple offsets for bold shadow)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if abs(dx) + abs(dy) >= 3:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))

        # Draw outline
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0))

        # Draw main white text
        draw.text((x, y), line, font=font, fill=SUBTITLE_COLOR)

        y += line_h

    return img


def _add_dark_vignette(pil_img):
    """Add subtle dark vignette + bottom gradient for cinematic look."""
    img = pil_img.copy().convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bottom gradient for subtitle readability
    grad_h = 600
    for y in range(grad_h):
        alpha = int(160 * (y / grad_h))
        draw.line([(0, HEIGHT - grad_h + y), (WIDTH, HEIGHT - grad_h + y)],
                  fill=(0, 0, 0, alpha))

    # Top gradient (subtle)
    for y in range(200):
        alpha = int(80 * (1 - y / 200))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


# ─────────────────────────────────────────────
#  Main Video Builder
# ─────────────────────────────────────────────

def build_video(audio_path, word_timings, image_paths, output_path):
    """
    Build final MP4 with:
    - Cycling background images
    - Reels-style 2-3 word synced subtitles
    - Full voiceover audio

    Args:
        audio_path   : Path to MP3 voice file
        word_timings : List of {word, start, duration} dicts
        image_paths  : List of background image paths
        output_path  : Output MP4 path

    Returns:
        output_path
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load audio to get total duration
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration + 0.5  # small buffer at end

    # Group words into subtitle chunks
    subtitle_groups = group_words_into_subtitles(word_timings, WORDS_PER_SUBTITLE)
    print(f"  📝 {len(subtitle_groups)} subtitle groups created")

    # Pre-load and prep background images
    print(f"  🖼️  Preparing {len(image_paths)} background(s)...")
    bg_images = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
        img = _add_dark_vignette(img)
        bg_images.append(img)

    # Each background shows for this many seconds
    secs_per_bg = total_duration / len(bg_images)

    def make_frame(t):
        """Generate a single video frame at time t."""
        # Pick background based on time
        bg_idx = min(int(t / secs_per_bg), len(bg_images) - 1)
        frame_img = bg_images[bg_idx].copy()

        # Find active subtitle at time t
        active_sub = None
        for group in subtitle_groups:
            if group["start"] <= t <= group["end"] + 0.05:
                active_sub = group["text"]
                break

        # Draw subtitle if active
        if active_sub:
            frame_img = _draw_subtitle_on_frame(frame_img, active_sub)

        return np.array(frame_img)

    # Build video clip
    print(f"  🎞️  Rendering {total_duration:.1f}s of video...")
    video = VideoClip(make_frame, duration=total_duration)
    video = video.set_fps(FPS)
    video = video.set_audio(audio_clip)

    # Write final MP4
    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        logger=None,
        threads=4,
    )

    video.close()
    audio_clip.close()

    return output_path
