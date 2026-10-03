#!/usr/bin/env bash
#
# 画面ロック（Waybar のロックボタン用）
#
# 【重要】niri / Hyprland のどちらでも動くように、実行時に WM を判定する。
# Hyprland 環境には hyprlock が入り swaylock は入らないことがあるため、
# "swaylock" 決め打ちだとボタンが無反応になる。
# hyprlock を参照しているので、install.sh の swaylock→hyprlock 置換の対象外になる。

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

if [ "$WM" = "hyprland" ] && command -v hyprlock >/dev/null 2>&1; then
    exec hyprlock
elif command -v swaylock >/dev/null 2>&1; then
    exec swaylock -f
elif command -v hyprlock >/dev/null 2>&1; then
    exec hyprlock
else
    notify-send "画面ロック" "画面ロックのコマンドが見つかりません"
fi
