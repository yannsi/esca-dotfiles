#!/usr/bin/env bash
#
# Waybar 電源メニュー（fuzzel ドロップダウン）
#
# 【重要】このスクリプトは niri / Hyprland のどちらでも動く。
# WM 名を決め打ちせず、実行時に環境変数と `command -v` で判定する。
# install.sh 側で sed 変換しなくて済むように、意図的にこの作りにしている。

# 既にfuzzelが起動している場合は閉じる（トグル動作）
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# ── 現在の WM を判定する ──
# 【重要】`command -v niri` だけで判定しないこと。
# niri と Hyprland を両方インストールしている環境では、Hyprland で
# ログインしていても niri コマンドが存在するため誤判定する。
# 実際に走っているセッションを見るには XDG_CURRENT_DESKTOP か
# 各 WM が出す固有の環境変数を使う。
detect_wm() {
    case "${XDG_CURRENT_DESKTOP:-}" in
        *Hyprland*|*hyprland*) echo "hyprland"; return ;;
        *niri*|*Niri*)         echo "niri";     return ;;
    esac
    # 環境変数が無い場合のフォールバック（インスタンス署名で判定）
    [ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ] && { echo "hyprland"; return; }
    [ -n "${NIRI_SOCKET:-}" ]                 && { echo "niri";     return; }
    echo "unknown"
}
WM=$(detect_wm)

# ── 画面ロック ──
# Hyprland は hyprlock、niri は swaylock を使う。
# どちらも無い場合に無反応で終わると「壊れている」ように見えるため通知を出す。
lock_screen() {
    if [ "$WM" = "hyprland" ] && command -v hyprlock >/dev/null 2>&1; then
        hyprlock
    elif command -v swaylock >/dev/null 2>&1; then
        swaylock -f
    elif command -v hyprlock >/dev/null 2>&1; then
        hyprlock
    else
        notify-send "電源メニュー" "画面ロックのコマンドが見つかりません"
    fi
}

# ── ログアウト ──
# 【重要】WM 固有の終了コマンドを優先すること。
# loginctl terminate-user はユーザーのプロセスを一斉に落とすため、
# 保存していない作業が失われやすい。最後の手段として残す。
logout_session() {
    if [ "$WM" = "hyprland" ] && command -v hyprctl >/dev/null 2>&1; then
        hyprctl dispatch exit
    elif [ "$WM" = "niri" ] && command -v niri >/dev/null 2>&1; then
        niri msg action quit --skip-confirmation
    else
        loginctl terminate-user "$USER"
    fi
}

# 電源メニューの選択肢
SELECTIONS="  画面ロック\n󰤄  サスペンド\n󰍃  ログアウト\n󰑐  再起動\n  シャットダウン"

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
        lock_screen
        ;;
    *"サスペンド"*)
        systemctl suspend
        ;;
    *"ログアウト"*)
        logout_session
        ;;
    *"再起動"*)
        systemctl reboot
        ;;
    *"シャットダウン"*)
        systemctl poweroff
        ;;
esac
