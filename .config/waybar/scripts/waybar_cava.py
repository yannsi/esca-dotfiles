#!/usr/bin/env python3
import sys
import subprocess
import os
import signal
import json
import tempfile

# Configuration
BARS_NUMBER = 10
BAR_CHARACTERS = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']

# Catppuccin Color Palettes
COLOR_PALETTES = [
    ("Default", "#bac2de"),
    ("Mauve", "#cba6f7"),
    ("Blue", "#89b4fa"),
    ("Teal", "#94e2d5"),
    ("Green", "#a6e3a1"),
    ("Yellow", "#f9e2af"),
    ("Peach", "#fab387"),
    ("Pink", "#f5c2e7"),
    ("Red", "#f38ba8"),
    ("Rainbow", ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5", "#89dceb", "#89b4fa", "#b4befe", "#cba6f7", "#f5c2e7"])
]

STATE_FILE = os.path.expanduser("~/.config/waybar/scripts/cava_color.txt")

# Load current color index
current_color_idx = 0
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            current_color_idx = int(f.read().strip()) % len(COLOR_PALETTES)
    except Exception:
        current_color_idx = 0

def handle_sigusr1(signum, frame):
    global current_color_idx
    current_color_idx = (current_color_idx + 1) % len(COLOR_PALETTES)
    try:
        with open(STATE_FILE, "w") as f:
            f.write(str(current_color_idx))
    except Exception:
        pass

signal.signal(signal.SIGUSR1, handle_sigusr1)

# Cava Configuration
config_content = f"""
[general]
framerate = 40
bars = {BARS_NUMBER}
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = {len(BAR_CHARACTERS) - 1}
"""

with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_config:
    tmp_config.write(config_content)
    config_path = tmp_config.name

try:
    process = subprocess.Popen(
        ['cava', '-p', config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        try:
            values = [v for v in line.strip().split(';') if v]
            if len(values) < BARS_NUMBER:
                continue

            name, color_def = COLOR_PALETTES[current_color_idx]

            if isinstance(color_def, list):
                # Rainbow mode: 各バーごとにグラデーションカラーを適用
                formatted_chars = []
                for i, v in enumerate(values[:BARS_NUMBER]):
                    idx = int(v)
                    idx = max(0, min(len(BAR_CHARACTERS) - 1, idx))
                    char = BAR_CHARACTERS[idx]
                    bar_color = color_def[i % len(color_def)]
                    formatted_chars.append(f"<span color='{bar_color}'>{char}</span>")
                output_text = "".join(formatted_chars)
            else:
                # 単色カラー
                chars = []
                for v in values[:BARS_NUMBER]:
                    idx = int(v)
                    idx = max(0, min(len(BAR_CHARACTERS) - 1, idx))
                    chars.append(BAR_CHARACTERS[idx])
                raw_str = "".join(chars)
                output_text = f"<span color='{color_def}'>{raw_str}</span>"

            data = {
                "text": output_text,
                "tooltip": f"CAVA: {name}（クリックで色変更）"
            }
            print(json.dumps(data), flush=True)

        except ValueError:
            pass

except KeyboardInterrupt:
    pass
finally:
    if os.path.exists(config_path):
        os.remove(config_path)
    if 'process' in locals() and process:
        process.terminate()
