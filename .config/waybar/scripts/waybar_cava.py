#!/usr/bin/env python3
"""
Waybar 用 CAVA オーディオビジュアライザ

【重要】waybar の custom モジュールは、スクリプトが何も出力しないまま
終了すると「モジュールごとバーから消える」。エラーメッセージも出ないため、
原因の特定が極めて難しい。
このスクリプトは次の2点を必ず守ること:

  1. 起動直後に必ず1行 JSON を出す（cava の準備を待たない）
  2. どんな失敗でも exit しない（再試行ループで粘る）

とくに 2 が重要。ログイン直後は pipewire-pulse がまだ起動しておらず、
cava が即座に終了することがある。従来版はそこで Python ごと落ちていたため、
「niri では出るのに Hyprland では出ない」といった再現性のない消え方をしていた。
"""
import sys
import subprocess
import os
import signal
import json
import tempfile
import time

# ── 設定 ──
BARS_NUMBER = 10
BAR_CHARACTERS = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
RETRY_WAIT = 5          # cava の起動に失敗したときの待ち時間（秒）
IDLE_CHAR = '▁'         # 音が鳴っていない/待機中に出す文字

# Catppuccin カラーパレット（クリックで循環）
COLOR_PALETTES = [
    ("Default", "#bac2de"),
    ("Mauve",   "#cba6f7"),
    ("Blue",    "#89b4fa"),
    ("Teal",    "#94e2d5"),
    ("Green",   "#a6e3a1"),
    ("Yellow",  "#f9e2af"),
    ("Peach",   "#fab387"),
    ("Pink",    "#f5c2e7"),
    ("Red",     "#f38ba8"),
    ("Rainbow", ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5",
                 "#89dceb", "#89b4fa", "#b4befe", "#cba6f7", "#f5c2e7"]),
]

STATE_FILE = os.path.expanduser("~/.config/waybar/scripts/cava_color.txt")

current_color_idx = 0
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            current_color_idx = int(f.read().strip()) % len(COLOR_PALETTES)
    except Exception:
        current_color_idx = 0


def handle_sigusr1(signum, frame):
    """クリック（pkill -SIGUSR1）で色を切り替える"""
    global current_color_idx
    current_color_idx = (current_color_idx + 1) % len(COLOR_PALETTES)
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            f.write(str(current_color_idx))
    except Exception:
        pass


signal.signal(signal.SIGUSR1, handle_sigusr1)


def emit(text, tooltip=None):
    """waybar へ1行 JSON を出す。ここが止まるとモジュールが消える。"""
    try:
        data = {"text": text}
        if tooltip:
            data["tooltip"] = tooltip
        print(json.dumps(data), flush=True)
    except BrokenPipeError:
        # waybar が終了した。これ以上書いても意味がないので静かに抜ける。
        sys.exit(0)


def colorize(chars):
    """現在のパレットで Pango マークアップを組み立てる"""
    name, color_def = COLOR_PALETTES[current_color_idx]
    if isinstance(color_def, list):
        parts = [
            "<span color='{}'>{}</span>".format(color_def[i % len(color_def)], c)
            for i, c in enumerate(chars)
        ]
        return "".join(parts), name
    return "<span color='{}'>{}</span>".format(color_def, "".join(chars)), name


def emit_idle(reason):
    """待機表示。cava が動いていなくてもモジュールを消さないための保険。"""
    text, name = colorize([IDLE_CHAR] * BARS_NUMBER)
    emit(text, "CAVA: {}（{}）".format(name, reason))


CONFIG_CONTENT = """
[general]
framerate = 40
bars = {bars}
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = {maxrange}
""".format(bars=BARS_NUMBER, maxrange=len(BAR_CHARACTERS) - 1)


def run_cava(config_path):
    """
    cava を起動して出力を流し続ける。
    正常終了・異常終了のどちらでも return する（例外は投げない）。
    """
    try:
        process = subprocess.Popen(
            ['cava', '-p', config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        # cava コマンド自体が無い。パッケージ未導入。
        emit_idle("cava が見つかりません")
        return
    except Exception as e:
        emit_idle("cava を起動できません: {}".format(type(e).__name__))
        return

    try:
        for line in process.stdout:
            values = [v for v in line.strip().split(';') if v]
            if len(values) < BARS_NUMBER:
                continue
            try:
                chars = []
                for v in values[:BARS_NUMBER]:
                    idx = max(0, min(len(BAR_CHARACTERS) - 1, int(v)))
                    chars.append(BAR_CHARACTERS[idx])
            except ValueError:
                continue
            text, name = colorize(chars)
            emit(text)
    except Exception:
        # 読み取り中の想定外エラーでも落ちない
        pass
    finally:
        try:
            process.terminate()
        except Exception:
            pass


def main():
    # 【重要】何より先に1行出す。ここを待たせるとモジュールが出ない。
    emit_idle("起動中")

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.conf') as tmp:
        tmp.write(CONFIG_CONTENT)
        config_path = tmp.name

    try:
        while True:
            run_cava(config_path)
            # cava が落ちた（音声サーバー未起動など）。待って再挑戦する。
            emit_idle("音声入力を待機中")
            time.sleep(RETRY_WAIT)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            os.remove(config_path)
        except Exception:
            pass


if __name__ == "__main__":
    main()
