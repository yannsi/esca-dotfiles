#!/usr/bin/env bash

# 既にfuzzelが起動している場合は閉じる（トグル動作）
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

ACTION="${1:-poweroff}"

case "$ACTION" in
    poweroff|shutdown)
        PROMPT="シャットダウンしますか？ ❯ "
        OPTION_EXEC="  シャットダウン"
        CMD="systemctl poweroff"
        ;;
    reboot)
        PROMPT="再起動しますか？ ❯ "
        OPTION_EXEC="  再起動"
        CMD="systemctl reboot"
        ;;
    suspend)
        PROMPT="サスペンドしますか？ ❯ "
        OPTION_EXEC="  サスペンド"
        CMD="systemctl suspend"
        ;;
    logout|quit)
        PROMPT="ログアウトしますか？ ❯ "
        OPTION_EXEC="󰗼  ログアウト"
        if command -v niri >/dev/null 2>&1; then
            CMD="niri msg action quit -s"
        else
            CMD="loginctl terminate-user $USER"
        fi
        ;;
    *)
        PROMPT="実行しますか？ ❯ "
        OPTION_EXEC="✓  実行"
        CMD="$ACTION"
        ;;
esac

OPTION_CANCEL="󰅖  キャンセル"

CHOSEN=$(echo -e "${OPTION_EXEC}\n${OPTION_CANCEL}" | fuzzel \
    --dmenu \
    --prompt="${PROMPT}" \
    --lines=2 \
    --width=26)

if [ "$CHOSEN" = "$OPTION_EXEC" ]; then
    eval "$CMD"
fi
