#!/usr/bin/env bash
#
# 壁紙変更（fuzzel で選択）
#
# 【重要】このスクリプトは niri / Hyprland のどちらでも動く。
# niri は swaybg、Hyprland は hyprpaper と壁紙デーモンが異なり、
# 起動方法も切り替え方法も違う。実行時に判定して使い分ける。

# 既にfuzzelが起動している場合は閉じる
if pgrep -x "fuzzel" > /dev/null; then
    pkill -x "fuzzel"
    exit 0
fi

# 画像ファイル候補を探す（ホームディレクトリ・Pictures・システムの壁紙置き場）
WALLPAPERS=$(find "$HOME/Pictures" "$HOME" /usr/share/backgrounds \
    -maxdepth 3 -type f \
    \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) \
    2>/dev/null | sort -u)

if [ -z "$WALLPAPERS" ]; then
    notify-send "Wallchange" "画像ファイルが見つかりませんでした"
    exit 1
fi

SELECTED=$(echo "$WALLPAPERS" | fuzzel --dmenu --prompt="🖼 壁紙を選択 ❯ " --lines=12 --width=60)

[ -z "$SELECTED" ] && exit 0

# ── 壁紙デーモンごとの適用 ──
apply_hyprpaper() {
    # 【重要】hyprpaper は preload してからでないと wallpaper を設定できない。
    # いきなり wallpaper を投げると「読み込まれていない」と拒否される。
    # また unload all を先に入れないと、切り替えるたびに画像がメモリに溜まる。
    hyprctl hyprpaper unload all      >/dev/null 2>&1
    hyprctl hyprpaper preload "$SELECTED"  >/dev/null 2>&1
    hyprctl hyprpaper wallpaper ",$SELECTED" >/dev/null 2>&1 || return 1

    # 次回ログイン時にも復元されるよう設定ファイルを更新する。
    # 【重要】hyprpaper.conf を書き換えるだけでは即時反映されない。
    # 上の hyprctl と両方が必要。
    mkdir -p "$HOME/.config/hypr"
    cat > "$HOME/.config/hypr/hyprpaper.conf" << EOF
preload = ${SELECTED}
wallpaper = ,${SELECTED}

ipc = on
splash = false
EOF
    return 0
}

apply_swaybg() {
    command -v swaybg >/dev/null 2>&1 || return 1
    # 再ログイン時に復元するための起動スクリプトを更新
    printf '#!/bin/bash\nswaybg -i %q -m fill &\n' "$SELECTED" \
        > "$HOME/.config/waybar/scripts/wallpaper"
    chmod +x "$HOME/.config/waybar/scripts/wallpaper"

    pkill -x swaybg 2>/dev/null
    swaybg -i "$SELECTED" -m fill &
    return 0
}

# hyprpaper が動いていればそちらを優先、なければ swaybg。
# 【重要】インストール済みかどうかではなく「動いているか」で判定すること。
# 両方入っている環境で、動いていない側に投げても壁紙は変わらない。
if pgrep -x hyprpaper >/dev/null 2>&1 && command -v hyprctl >/dev/null 2>&1; then
    apply_hyprpaper && ok=1
elif pgrep -x swaybg >/dev/null 2>&1; then
    apply_swaybg && ok=1
else
    # どちらも起動していない場合は、入っているほうを使って新規に起動する
    if command -v hyprctl >/dev/null 2>&1 && command -v hyprpaper >/dev/null 2>&1; then
        hyprpaper >/dev/null 2>&1 &
        sleep 1
        apply_hyprpaper && ok=1
    else
        apply_swaybg && ok=1
    fi
fi

if [ "${ok:-0}" = "1" ]; then
    notify-send "Wallchange" "壁紙を変更しました"
else
    notify-send "Wallchange" "壁紙デーモン (hyprpaper / swaybg) が見つかりませんでした"
    exit 1
fi

exit 0
