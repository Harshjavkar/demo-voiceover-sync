# Demo Video Voiceover Sync

Automatically generate natural-sounding neural voiceovers and sync them to exact video timestamps using `edge-tts` and `ffmpeg`—with zero timeline drift and broadcast loudness normalization (`-16 LUFS`).

## Features
- **Exact Timestamp Sync:** Anchors each narration segment to exact millisecond offsets via `ffmpeg` `adelay` + `amix` filters.
- **Broadcast Loudness:** Normalizes final audio to `-16 LUFS` (`loudnorm`) for consistent playback across laptops and conference rooms.
- **Zero Video Re-encoding:** Copies the original H.264/HEVC video stream (`-c:v copy`) for lossless visual quality and fast rendering.
- **Free & Unlimited:** Uses neural TTS voices without character limits or watermarks.

## Prerequisites
- Python 3.9+
- `ffmpeg` installed and available in your system `PATH`

## Setup & Usage

```bash
pip install -r requirements.txt
python generate_voiceover.py --video demo-video.mp4 --output final_demo.mp4
```

### Custom Script JSON Format
Create a `scenes.json` file with `[start_seconds, "narration text"]` pairs:

```json
[
  [0.5, "Welcome to the product walkthrough."],
  [15.0, "Next, let's look at the real-time analytics dashboard."]
]
```

Run with your custom script and voice:
```bash
python generate_voiceover.py --video demo.mp4 --script scenes.json --voice en-US-AndrewNeural
```
