"""Build the browser version of the game with pygbag.

Run:  python build_web.py
Needs: pip install pygbag
The finished site is written to build/flappypie/build/web.
"""
import shutil
import subprocess
import sys
from pathlib import Path

TITLE = "FlappyPie - Play Free Online, No Download"
DESCRIPTION = ("Play FlappyPie online for free. No download, no signup. "
               "Tap to flap, dodge the pipes and beat your high score.")

ROOT = Path(__file__).parent
STAGE = ROOT / "build" / "flappypie"

# Copy only what the game needs, so private files can never end up on the website.
shutil.rmtree(STAGE, ignore_errors=True)
(STAGE / "audio").mkdir(parents=True)
shutil.copy(ROOT / "main.py", STAGE)
shutil.copy(ROOT / "LICENSE-flappy-bird-assets.txt", STAGE)
shutil.copytree(ROOT / "sprites", STAGE / "sprites")
for sound in (ROOT / "audio").glob("*.ogg"):
    shutil.copy(sound, STAGE / "audio")

subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", "FlappyPie", str(STAGE)], check=True)

# Google shows the title, description and icon set here.
site = STAGE / "build" / "web"
page = site / "index.html"
html = page.read_text(encoding="utf-8")
html = html.replace("<title>FlappyPie</title>",
                    f'<title>{TITLE}</title>\n    <meta name="description" content="{DESCRIPTION}">')
html = html.replace('href="favicon.png" sizes="16x16"', 'href="favicon.png" sizes="96x96"')
page.write_text(html, encoding="utf-8")
shutil.copy(ROOT / "favicon.png", site / "favicon.png")

print("Site ready in", site)
