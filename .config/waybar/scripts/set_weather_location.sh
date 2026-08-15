#!/bin/bash

CONFIG_FILE="$HOME/.config/waybar/scripts/weather_location.txt"

# 既にfuzzelが起動している場合は閉じる
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# 代表的な都市のプリセット一覧（直接文字入力で任意の都市・地域名も指定可能）
CITIES=$(cat << 'EOF'
那覇 (Naha)
沖縄 (Okinawa)
名護 (Nago)
石垣 (Ishigaki)
宮古島 (Miyakojima)
東京 (Tokyo)
大阪 (Osaka)
京都 (Kyoto)
名古屋 (Nagoya)
福岡 (Fukuoka)
札幌 (Sapporo)
仙台 (Sendai)
広島 (Hiroshima)
New_York (ニューヨーク)
London (ロンドン)
Paris (パリ)
Seoul (ソウル)
Taipei (台北)
Sydney (シドニー)
EOF
)

# fuzzelで選択または自由入力
SELECTED=$(echo "$CITIES" | fuzzel --dmenu --prompt="📍 天気の地域設定 ❯ " --lines=12 --width=35)

# キャンセルされた場合は終了
[ -z "$SELECTED" ] && exit 0

# 都市名の抽出（先頭の単語を取り出す）
NEW_CITY=$(echo "$SELECTED" | awk '{print $1}')

# 入力内容をファイルに保存
echo "$NEW_CITY" > "$CONFIG_FILE"

# 通知を表示
notify-send "Weather Update" "天気の地域を「$NEW_CITY」に設定しました"

# Waybarの天気モジュールにシグナルを送って即時更新
pkill -RTMIN+9 waybar 2>/dev/null

exit 0
