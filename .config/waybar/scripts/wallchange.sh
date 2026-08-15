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
    # 【重要】preload は現在の hyprpaper では廃止されている。
    # 旧来の「preload してから wallpaper」という手順は不要で、
    # wallpaper リクエストに "<出力>,<パス>,<fit_mode>" を渡すだけでよい。
    # 出力名を空にすると全ディスプレイが対象になる。fit_mode は省略可。
    # 自分の版が受け付けるリクエストは hyprctl hyprpaper --help で確認できる。
    hyprctl hyprpaper wallpaper ",$SELECTED,cover" >/dev/null 2>&1 || return 1

    # 次回ログイン時にも復元されるよう設定ファイルを更新する。
    # 【重要】hyprpaper.conf を書き換えるだけでは即時反映されない。
    # 上の hyprctl と両方が必要。
    # 【重要】書式はブロック形式。preload = / wallpaper = ,path の旧書式で
    # 書くと解釈されず、次回ログイン時に背景が真っ黒になる。
    mkdir -p "$HOME/.config/hypr"
    cat > "$HOME/.config/hypr/hyprpaper.conf" << EOF
wallpaper {
    monitor =
    path = ${SELECTED}
    fit_mode = cover
}

ipc = true
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
