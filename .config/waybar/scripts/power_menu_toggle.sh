#!/usr/bin/env bash

# 既にfuzzelが起動している場合は閉じる（トグル動作）
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# 電源メニューの選択肢
SELECTIONS="  画面ロック\n󰤄  サスペンド\n󰍃  ログアウト\n󰑐  再起動\n  シャットダウン"

# Waybarの電源ボタン直下（右上）にドロップダウン風に小さく表示
CHOSEN=$(echo -e "$SELECTIONS" | fuzzel \
    --dmenu \
    --prompt="⏻  " \
    --anchor=top-right \
    --x-margin=16 \
    --y-margin=38 \
    --lines=5 \
    --width=18)

# キャンセルされた場合は終了
[ -z "$CHOSEN" ] && exit 0

case "$CHOSEN" in
    *"画面ロック"*)
        swaylock
        ;;
    *"サスペンド"*)
        systemctl suspend
        ;;
    *"ログアウト"*)
        if command -v niri >/dev/null 2>&1; then
            niri msg action quit --skip-confirmation
        else
            loginctl terminate-user "$USER"
        fi
        ;;
    *"再起動"*)
        systemctl reboot
        ;;
    *"シャットダウン"*)
        systemctl poweroff
        ;;
esac
