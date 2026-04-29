import os
import sys
from voice_gen import generate_voice_with_timings
from image_gen import generate_images_for_story
from video_builder import build_video

def main():
    print("=" * 52)
    print("  🎬 YouTube Shorts Story Video Generator")
    print("  Reels-Style Subtitles Edition")
    print("=" * 52)

    # ── Get Script ──────────────────────────────────
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
        with open(script_file, 'r', encoding='utf-8') as f:
            script = f.read().strip()
        print(f"\n📄 Script loaded from: {script_file}")
    else:
        print("\n📝 Paste your full story script below.")
        print("   (Press Enter twice when done)\n")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        script = " ".join(lines).strip()

    if not script:
        print("❌ No script provided. Exiting.")
        return

    # ── Output Filename ──────────────────────────────
    output_name = input("\n📁 Output filename (without .mp4): ").strip()
    if not output_name:
        output_name = "story_video"
    output_path = os.path.join("output", f"{output_name}.mp4")
    os.makedirs("output", exist_ok=True)

    print(f"\n🎙️  Generating voiceover + syncing subtitles...")
    try:
        audio_path, word_timings = generate_voice_with_timings(script)
        print(f"   ✅ Voice generated ({len(word_timings)} words timed)")
    except Exception as e:
        print(f"   ❌ Voice generation failed: {e}")
        return

    print(f"\n🖼️  Generating background images...")
    try:
        image_paths = generate_images_for_story(script)
        print(f"   ✅ {len(image_paths)} background image(s) ready")
    except Exception as e:
        print(f"   ❌ Image generation failed: {e}")
        return

    print(f"\n🎬 Building video with Reels-style subtitles...")
    try:
        final_path = build_video(audio_path, word_timings, image_paths, output_path)
        print(f"\n{'=' * 52}")
        print(f"  ✅ VIDEO READY!")
        print(f"  📁 Saved to: {final_path}")
        print(f"  🚀 Upload directly to YouTube Shorts!")
        print(f"{'=' * 52}")
    except Exception as e:
        print(f"\n❌ Video build failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
