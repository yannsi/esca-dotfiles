#!/bin/sh
# 使い方: screenshot.sh [area|screen]   （既定: area=範囲選択）
# 保存先は xdg-user-dir が返す「ピクチャ」ディレクトリ（日本語名でもOK）。
#
# install.sh が ~/.local/bin/screenshot.sh に書き出すものと同じ動作。
# dotfiles を setup.sh でリンクしただけの環境でも PrintScreen が効くように、
# hyprland.lua からはこちらを呼ぶ（必要: grim slurp wl-clipboard）。
mode="${1:-area}"

# ピクチャディレクトリを解決（未設定なら $HOME/ピクチャ を使う）
pic_dir="$(xdg-user-dir PICTURES 2>/dev/null)"
[ -z "$pic_dir" ] && pic_dir="$HOME/ピクチャ"
save_dir="$pic_dir/スクリーンショット"
mkdir -p "$save_dir"

file="$save_dir/$(date +%Y-%m-%d_%H-%M-%S).png"

case "$mode" in
  screen) grim "$file" ;;
  *)      grim -g "$(slurp)" "$file" ;;
esac

# 撮影に成功したらクリップボードにもコピーし、通知を出す
if [ -f "$file" ]; then
  wl-copy < "$file" 2>/dev/null || true
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "スクリーンショット" "保存しました: $file" || true
  fi
fi
