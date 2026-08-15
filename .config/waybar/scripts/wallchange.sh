#!/bin/bash

# 既にfuzzelが起動している場合は閉じる
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# 画像ファイル候補を探す（ホームディレクトリおよびPictures）
WALLPAPERS=$(find "$HOME/Pictures" "$HOME" -maxdepth 2 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) 2>/dev/null)

if [ -z "$WALLPAPERS" ]; then
    notify-send "Wallchange" "画像ファイルが見つかりませんでした"
    exit 1
fi

SELECTED=$(echo "$WALLPAPERS" | fuzzel --dmenu --prompt="🖼 壁紙を選択 ❯ " --lines=12 --width=60)

[ -z "$SELECTED" ] && exit 0

echo '#!/bin/bash' > "$HOME/.config/waybar/scripts/wallpaper"
echo "swaybg -i '$SELECTED' &" >> "$HOME/.config/waybar/scripts/wallpaper"

killall swaybg 2>/dev/null
swaybg -i "$SELECTED" &

notify-send "Wallchange" "壁紙を変更しました"
exit 0
