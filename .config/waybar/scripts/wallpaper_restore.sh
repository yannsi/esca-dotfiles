#!/usr/bin/env bash
#
# ログイン時に壁紙を復元する（niri / Hyprland 共通）
#
# wallchange.sh で選んだ壁紙は、設定ファイルではなく状態ファイル
#   ${XDG_STATE_HOME:-~/.local/state}/esca/wallpaper
# に絶対パス1行で保存される。ここではそれを読んで壁紙デーモンに渡す。
#
# 【重要】選んだ壁紙を hyprpaper.conf や niri の config.kdl に書き込まないこと。
# setup.sh で ~/.config からリポジトリへリンクしている環境では、それは
# リポジトリ内のファイルそのもので、壁紙を変えるたびに差分が出て
# git pull が衝突する。設定は既定値、選択結果は状態ファイル、と分ける。
#
# 自動起動の書き方:
#   niri     : spawn-at-startup "sh" "-c" "bash $HOME/.config/waybar/scripts/wallpaper_restore.sh"
#   Hyprland : hl.exec_cmd("bash $HOME/.config/waybar/scripts/wallpaper_restore.sh")

STATE_FILE="${XDG_STATE_HOME:-$HOME/.local/state}/esca/wallpaper"
DEFAULT_WALLPAPER="/usr/share/backgrounds/esca/esca.png"
# 画像が一枚も無いときの塗りつぶし色（インストーラの既定と同じ Esca の背景色）
DEFAULT_COLOR="#0d182c"

case "${XDG_CURRENT_DESKTOP:-}" in
    *Hyprland*|*hyprland*) WM="hyprland" ;;
    *niri*|*Niri*)         WM="niri" ;;
    *)
        if [ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]; then WM="hyprland"
        elif [ -n "${NIRI_SOCKET:-}" ]; then WM="niri"
        else WM="unknown"
        fi
        ;;
esac

# 保存された壁紙（画像が消えていたら無視する）
saved=""
if [ -f "$STATE_FILE" ]; then
    IFS= read -r saved < "$STATE_FILE"
    [ -f "$saved" ] || saved=""
fi

if [ "$WM" = "hyprland" ]; then
    # 保存が無ければ hyprpaper.conf の既定のままでよい
    [ -n "$saved" ] || exit 0
    # 【重要】hyprpaper は Hyprland の自動起動で同時に立ち上がるため、
    # すぐには IPC が受け付けられない。成功するまで少し待ちながら繰り返す。
    for _ in $(seq 1 20); do
        if hyprctl hyprpaper wallpaper ",$saved,cover" >/dev/null 2>&1; then
            exit 0
        fi
        sleep 0.5
    done
    exit 1
fi

# niri など（swaybg）
command -v swaybg >/dev/null 2>&1 || exit 0

# 【重要】先に起動した swaybg を止めてから起動すること。
# インストーラが config.kdl に固定画像の swaybg を追記している環境では、
# ログイン時に swaybg が二つ同時に起動し、どちらが手前に出るかが不定になる。
# 同時起動に間に合うよう少し待ってから止める。
sleep 1
pkill -x swaybg 2>/dev/null

if [ -n "$saved" ]; then
    exec swaybg -i "$saved" -m fill
elif [ -f "$DEFAULT_WALLPAPER" ]; then
    exec swaybg -i "$DEFAULT_WALLPAPER" -m fill
else
    exec swaybg -c "$DEFAULT_COLOR"
fi
