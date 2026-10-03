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
        # 【重要】`command -v niri` で判定しないこと。niri と Hyprland を両方
        # 入れた環境では、Hyprland でログインしていても niri 側の終了コマンドが
        # 選ばれ、ログアウトできなくなる。実際に走っているセッションで判定する。
        # （判定方法は power_menu_toggle.sh と同じ）
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
        if [ "$WM" = "hyprland" ] && command -v hyprctl >/dev/null 2>&1; then
            CMD="hyprctl dispatch exit"
        elif [ "$WM" = "niri" ] && command -v niri >/dev/null 2>&1; then
            CMD="niri msg action quit --skip-confirmation"
        else
            CMD="loginctl terminate-user \"\$USER\""
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
