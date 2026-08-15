#!/bin/bash

STATION_FILE="$HOME/.config/waybar/scripts/Radiostation.txt"

# 既にfuzzelが起動している場合は閉じる（トグル動作）
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# 局名リストの作成（先頭に停止項目を追加）
# fuzzel の dmenu モードで局を選択
selected=$( (echo "⏹  停止 (Stop Radio)"; awk '{print $1}' "$STATION_FILE") | fuzzel --dmenu --prompt="📻 Radio ❯ " --lines=18 --width=48 )

# キャンセルされた場合は終了
[ -z "$selected" ] && exit 0

# 既存のラジオ再生プロセスを停止
pkill -x mpv 2>/dev/null

# 「停止」が選ばれた場合はここで終了
if [ "$selected" = "⏹  停止 (Stop Radio)" ]; then
    exit 0
fi

# 選択された局名に対応するURLを取得
url=$(awk -v sel="$selected" '$1 == sel {print $2}' "$STATION_FILE")

[ -z "$url" ] && exit 0

# 局に応じた再生処理
if [ "$url" = "https://radiko.jp/#!/live/RN2" ]; then
    streamlink --player mpv 'https://radiko.jp/#!/live/RN2' best &
elif [ "$url" = "https://radiko.jp/#!/live/FM_OKINAWA" ]; then
    firefox --new-window 'https://radiko.jp/#!/live/FM_OKINAWA' &
else
    mpv "$url" &
fi

exit 0
