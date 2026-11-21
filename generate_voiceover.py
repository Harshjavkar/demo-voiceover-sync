import argparse
import asyncio
import json
import os
import subprocess
import tempfile
import edge_tts

DEFAULT_SCENES = [
    (0.5, "Cognify starts with a frictionless, security-first sign-in. Credentials are validated independently, passwords are never exposed in the client, and sessions live inside hardened HTTP-only cookies—welcoming learners immediately into their personal workspace."),
    (24.5, "Here is Maya’s command center. Daily XP goals, streaks, and curated worlds spanning technology, culinary arts, music, and science sit alongside open-ended topic search—turning curiosity into a structured daily habit."),
    (52.5, "Once a learner picks a topic, Cognify adapts to their confidence level. Guided Learning Mode builds intuition from first principles, while Quiz Mode jumps straight into dynamic assessment—respecting both beginners and advanced learners."),
    (76.5, "Inside Learning Mode, our AI tutor breaks down complex concepts like React Hooks into clear mental models, pairs them with live interactive code, and verifies comprehension with an instant knowledge check before moving forward."),
    (100.5, "In Quiz Mode, every ten-question session is dynamically assembled on the server—randomizing question order, distractors, and answer keys securely on the backend. Notice the avatar only commits after a deliberate tap, eliminating accidental clicks."),
    (128.5, "For technical domains, Cognify goes beyond trivia into code reading and output prediction. Here, the learner traces an array map transformation, receiving immediate visual validation and a concise explanation that reinforces the underlying logic."),
    (152.5, "Because real-world skills aren't just text, our assessment engine adapts its media to the domain. In practical cooking modules, visual illustrations pair with safety and sequencing challenges—teaching learners to read the full recipe before turning on a burner."),
    (180.5, "In music modules, learners interact directly with embedded audio and live waveforms to train rhythm and ear recognition without timer anxiety—while maintaining full text equivalents for universal accessibility."),
    (204.5, "Meet Nova, our context-aware AI companion. Because Nova sees the active lesson, recent accuracy, and current round, it delivers targeted mental models and hands-on cleanup exercises—and seamlessly falls back to authored guidance when offline, never hallucinating."),
    (236.5, "Our analytics engine separates gamified engagement from true mastery. Learners track active hours, streaks, and topic accuracy, while our diagnostic model pinpoints the lowest-confidence skill—like rhythm—to guide high-impact review."),
    (260.5, "With one click, learners export a clean, shareable PDF progress report generated directly from authorized session data—packaging topic scores, growth trends, and milestones for mentors, educators, or employers."),
    (288.5, "Every session closes with clear feedback and momentum—converting XP, coins, and diagnostic insights into the next learning step. That is Cognify: an adaptive, multimodal learning platform built for measurable mastery.")
]


async def render_video(video_path: str, output_path: str, voice: str, scenes: list[tuple[float, str]]) -> None:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video not found: {video_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        inputs = ["-i", video_path]
        filter_parts = []
        mix_labels = []

        for idx, (start_sec, text) in enumerate(scenes):
            clip_path = os.path.join(tmpdir, f"scene_{idx:02d}.mp3")
            communicate = edge_tts.Communicate(text, voice, rate="-3%", pitch="+0Hz")
            await communicate.save(clip_path)

            inputs.extend(["-i", clip_path])
            delay_ms = int(start_sec * 1000)
            filter_parts.append(f"[{idx + 1}:a]adelay={delay_ms}|{delay_ms},apad[a{idx}]")
            mix_labels.append(f"[a{idx}]")

        n = len(scenes)
        filter_complex = (
            ";".join(filter_parts)
            + f";{''.join(mix_labels)}amix=inputs={n}:duration=longest:normalize=0,"
            + "loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
        )

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path,
        ]
        subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync neural TTS voiceovers onto demo videos using exact timestamps.")
    parser.add_argument("--video", required=True, help="Path to input MP4 demo video")
    parser.add_argument("--output", default="output_with_voiceover.mp4", help="Path to output MP4 file")
    parser.add_argument("--voice", default="en-US-AvaNeural", help="Edge-TTS neural voice ID")
    parser.add_argument("--script", help="Optional JSON file containing [[start_seconds, text], ...]")
    args = parser.parse_args()

    scenes = DEFAULT_SCENES
    if args.script:
        with open(args.script, "r", encoding="utf-8") as f:
            scenes = [(float(item[0]), str(item[1])) for item in json.load(f)]

    asyncio.run(render_video(args.video, args.output, args.voice, scenes))
    print(f"Exported synced video to: {args.output}")


if __name__ == "__main__":
    main()
