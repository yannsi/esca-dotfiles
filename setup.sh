#!/bin/bash
#
# esca-dotfiles のセットアップ
# ~/.config/<app> から、このリポジトリ内の設定へシンボリックリンクを張る。

# dotfiles のディレクトリ
# 【重要】~/dotfiles 決め打ちにしないこと。README と違う場所に clone した場合に
# 存在しないパスへのリンク（＝全部壊れたリンク）が黙って作られる。
# スクリプト自身の置き場所から求める。環境変数 DOTFILES_DIR で上書きも可。
DOTFILES_DIR="${DOTFILES_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
CONFIG_DIR="$HOME/.config"

echo "Setting up dotfiles from $DOTFILES_DIR ..."

# .configディレクトリがない場合は作成
mkdir -p "$CONFIG_DIR"

# リンクを作成する関数
link_config() {
    local target="$1"
    local link_name="$2"
    local src="$DOTFILES_DIR/.config/$target"
    local dest="$CONFIG_DIR/$link_name"

    # 【重要】リンク元がリポジトリに無いものは何もしないこと。
    # 先に既存設定を .bak へ退避してから壊れたリンクを張ると、
    # 動いていた設定が消えたように見える（以前の wlogout がこれだった）。
    if [ ! -e "$src" ]; then
        echo "Skipped $target (not in this repository)"
        return 0
    fi

    # 既にディレクトリやファイルがある場合はバックアップ
    # 既存の .bak を上書き・入れ子にしないよう日時を付ける
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        local backup
        backup="$dest.bak.$(date +%Y%m%d-%H%M%S)"
        echo "Backing up existing $link_name to $backup"
        mv "$dest" "$backup"
    fi

    # シンボリックリンクの作成（上書き強制、-nでディレクトリリンクの追跡防止）
    ln -sfn "$src" "$dest"
    echo "Linked $target -> $dest"
}

# リストにある設定をリンク
link_config "niri" "niri"
link_config "hypr" "hypr"
link_config "waybar" "waybar"
link_config "alacritty" "alacritty"
link_config "fuzzel" "fuzzel"
link_config "swaylock" "swaylock"
link_config "starship.toml" "starship.toml"

echo "Setup complete! Please restart your shell or logout/login."
