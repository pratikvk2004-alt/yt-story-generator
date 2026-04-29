import requests
import os
import time
import random
from urllib.parse import quote
from PIL import Image, ImageDraw
from config import WIDTH, HEIGHT, ASSETS_DIR, IMAGE_STYLE, NUM_IMAGES


def _extract_story_keywords(script):
    """Extract key emotional/visual themes from script for better image prompts."""
    script_lower = script.lower()

    themes = []
    if any(w in script_lower for w in ["family", "mother", "father", "brother", "sister"]):
        themes.append("family drama")
    if any(w in script_lower for w in ["betray", "revenge", "anger", "hate"]):
        themes.append("dramatic confrontation, emotional tension")
    if any(w in script_lower for w in ["love", "heart", "romance"]):
        themes.append("emotional love story")
    if any(w in script_lower for w in ["peace", "calm", "happy", "joy"]):
        themes.append("peaceful resolution")
    if any(w in script_lower for w in ["dark", "night", "shadow", "fear"]):
        themes.append("dark moody atmosphere")

    if not themes:
        themes.append("dramatic human story, emotional")

    return ", ".join(themes)


def _try_pollinations(prompt, index):
    """Try Pollinations.ai."""
    models = ["flux", "turbo"]
    encoded = quote(prompt)
    for model in models:
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width={WIDTH}&height={HEIGHT}"
            f"&nologo=true&seed={index * 73}&model={model}"
        )
        try:
            r = requests.get(url, timeout=90)
            if r.status_code == 200:
                return r.content
        except Exception:
            pass
        time.sleep(2)
    return None


def _make_gradient_bg(index):
    """Beautiful fallback gradient background."""
    palettes = [
        [(10, 10, 30), (40, 10, 60), (80, 20, 80)],
        [(5, 15, 40), (10, 40, 80), (20, 60, 120)],
        [(30, 5, 5), (80, 10, 10), (140, 20, 20)],
        [(5, 25, 15), (10, 60, 30), (20, 100, 50)],
    ]
    colors = palettes[index % len(palettes)]
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        r = colors[0][0] + int((colors[2][0] - colors[0][0]) * y / HEIGHT)
        g = colors[0][1] + int((colors[2][1] - colors[0][1]) * y / HEIGHT)
        b = colors[0][2] + int((colors[2][2] - colors[0][2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    # Decorative circles
    for _ in range(6):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        rad = random.randint(80, 300)
        c = (min(255, colors[2][0]+30), min(255, colors[2][1]+30), min(255, colors[2][2]+30))
        draw.ellipse([x-rad, y-rad, x+rad, y+rad], outline=c, width=2)
    return img


def generate_images_for_story(script):
    """
    Generate NUM_IMAGES background images for the story video.
    Returns list of image file paths.
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    keywords = _extract_story_keywords(script)
    image_paths = []

    # Different prompts for visual variety throughout the video
    prompt_variations = [
        f"{keywords}, establishing shot, wide angle, {IMAGE_STYLE}",
        f"{keywords}, close up emotional face, {IMAGE_STYLE}",
        f"{keywords}, dramatic moment, tension, {IMAGE_STYLE}",
        f"{keywords}, resolution scene, cinematic ending, {IMAGE_STYLE}",
    ]

    for i in range(NUM_IMAGES):
        img_path = os.path.join(ASSETS_DIR, f"bg_{i:02d}.jpg")
        prompt = prompt_variations[i % len(prompt_variations)]

        print(f"   Generating image {i+1}/{NUM_IMAGES}...")
        content = _try_pollinations(prompt, i)

        if content:
            with open(img_path, "wb") as f:
                f.write(content)
            # Ensure correct size
            img = Image.open(img_path).convert("RGB")
            img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
            img.save(img_path, quality=95)
            print(f"   ✅ Image {i+1} ready")
        else:
            print(f"   ⚠️  API unavailable, using gradient background")
            img = _make_gradient_bg(i)
            img.save(img_path, quality=95)

        image_paths.append(img_path)

    return image_paths
