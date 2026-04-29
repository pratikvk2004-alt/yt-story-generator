import asyncio
import os
import edge_tts
from config import ASSETS_DIR, VOICE


async def _generate_async(text):
    """
    Generate voice audio AND capture word-level timings.
    edge-tts WordBoundary events give us exact timestamps for each word.
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    audio_path = os.path.join(ASSETS_DIR, "full_voice.mp3")

    communicate = edge_tts.Communicate(text, VOICE)
    word_timings = []
    audio_chunks = []

    async for event in communicate.stream():
        if event["type"] == "audio":
            audio_chunks.append(event["data"])
        elif event["type"] == "WordBoundary":
            word_timings.append({
                "word":     event["text"],
                "start":    event["offset"] / 10_000_000,    # ticks → seconds
                "duration": event["duration"] / 10_000_000,  # ticks → seconds
            })

    # Save audio
    with open(audio_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    return audio_path, word_timings


def generate_voice_with_timings(text):
    """
    Synchronous wrapper. Returns (audio_path, word_timings).
    word_timings = [{"word": str, "start": float, "duration": float}, ...]
    """
    try:
        return asyncio.run(_generate_async(text))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_generate_async(text))
