"""
Collect YouTube video transcripts using the Supadata API
and save them as markdown files.
"""

import os
import re
from pathlib import Path

from supadata import Supadata
from supadata.errors import SupadataError

OUTPUT_DIR = Path(__file__).parent / "RESEARCH" / "YouTube-Transcripts"


def get_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL."""
    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return "transcript"


def main() -> None:
    api_key = os.environ.get("SUPADATA_API_KEY")
    if not api_key:
        api_key = input("Enter your Supadata API key: ").strip()
    if not api_key:
        print("Error: API key is required. Get one at https://dash.supadata.ai")
        return

    url = input("Paste the YouTube video URL: ").strip()
    if not url:
        print("Error: No URL provided.")
        return

    print("Fetching transcript...")
    supadata = Supadata(api_key=api_key)

    try:
        result = supadata.youtube.transcript(url)
    except SupadataError as error:
        print(f"Error: {error.message}")
        return

    if not hasattr(result, "content"):
        print("Error: Transcript is still processing. Try again in a moment.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    video_id = get_video_id(url)
    filename = f"{video_id}.md"
    filepath = OUTPUT_DIR / filename

    language = getattr(result, "lang", "unknown")
    markdown = f"""# YouTube Transcript

**Video URL:** {url}
**Language:** {language}

---

{result.content}
"""

    filepath.write_text(markdown, encoding="utf-8")
    print(f"Saved to: {filepath}")


if __name__ == "__main__":
    main()
