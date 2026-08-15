#!/bin/bash

# dotfilesのディレクトリ
DOTFILES_DIR="$HOME/dotfiles"
CONFIG_DIR="$HOME/.config"

echo "Setting up dotfiles..."

# .configディレクトリがない場合は作成
mkdir -p "$CONFIG_DIR"

# リンクを作成する関数
link_config() {
    target="$1"
    link_name="$2"

    # 既にディレクトリやファイルがある場合はバックアップ
    if [ -e "$CONFIG_DIR/$link_name" ] && [ ! -L "$CONFIG_DIR/$link_name" ]; then
        echo "Backing up existing $link_name to $link_name.bak"
        mv "$CONFIG_DIR/$link_name" "$CONFIG_DIR/$link_name.bak"
    fi

    # シンボリックリンクの作成（上書き強制、-nでディレクトリリンクの追跡防止）
    ln -sfn "$DOTFILES_DIR/.config/$target" "$CONFIG_DIR/$link_name"
    echo "Linked $target -> $CONFIG_DIR/$link_name"
}

# リストにある設定をリンク
link_config "niri" "niri"
link_config "hypr" "hypr"
link_config "waybar" "waybar"
link_config "alacritty" "alacritty"
link_config "fuzzel" "fuzzel"
link_config "swaylock" "swaylock"
link_config "wlogout" "wlogout"
link_config "starship.toml" "starship.toml"

echo "Setup complete! Please restart your shell or logout/login."
