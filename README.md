# esca-dotfiles

Esca Linux（Arch Linux ベース）の Niri / Hyprland デスクトップ環境の設定ファイル集です。
[esca_linux_installer](https://github.com/yannsi/esca_linux_installer) の「GitHub から取得する」を選ぶと、このリポジトリの内容がインストール時に適用されます。
配色は Esca テーマ（アンコウの発光をイメージしたフィラメントブルー）が基本で、Swaylock などの一部は Catppuccin Macchiato ベースです。

## 収録されている設定

- **Window Manager**: Niri, Hyprland (`.config/hypr/hyprland.lua`)
- **Status Bar**: Waybar（Fuzzelラジオ、Chrome/Firefoxランチャー、カレンダー、天気予報、CAVAビジュアライザー内蔵）
- **Terminal**: Alacritty
- **Launcher**: Fuzzel
- **Screen Locker**: Swaylock（niri）/ Hyprlock（Hyprland）※ロック・ログアウトは実行中の WM を判定して切り替え
- **自動ロック**: 30分操作がなければロック、60分でサスペンド（niri: swayidle / Hyprland: hypridle）
- **壁紙**: swaybg（niri）/ hyprpaper（Hyprland）
- **Shell Prompt**: Starship

### ルートにあるファイル

| ファイル | 内容 |
|---|---|
| `esca` | Esca の既定壁紙（PNG）。インストーラがこのファイル名で直接取得するため、**名前を変えないこと** |
| `coffee` / `aisumicha` | テーマ別の壁紙（JPEG） |
| `sddm-coffee` / `sddm-aisumicha` | テーマ別の SDDM ログイン画面の背景（JPEG） |
| `kakishibu` / `sddm-kakishibu` | 柿渋テーマ用の置き場所（画像は未作成） |
| `EscaSymbols.otf` | Esca ロゴのグリフ（U+100000）を収めたフォント |

---

## 主な機能と操作方法

### Waybar の各モジュール
- **メニュー（  ）**: Fuzzel アプリケーションランチャーを起動
- **ブラウザ（  /  ）**: Firefox / Google Chrome をワンクリック起動（Chrome未インストール時は自動非表示）
- **インターネットラジオ（  ）**:
  - **左クリック**: Fuzzel で作業用BGM・ジャズ・クラシック・アニソン等の局を選択して再生
  - **右クリック**: 再生中のラジオを即時停止
- **メディア情報**: 再生中の楽曲・動画タイトルの表示と操作（クリックで再生/一時停止、右クリックで停止、中クリックでCAVA）
- **音量 / 輝度**: マウスホイールで直感的に音量・明るさを調整
- **天気予報**: 現在の気温・天気を表示（右クリックで地域変更ダイアログ）
- **壁紙の変更**: `scripts/wallchange.sh` で選んだ壁紙は `~/.local/state/esca/wallpaper` に保存され、次回ログイン時に `wallpaper_restore.sh` が復元します（リポジトリ内の設定ファイルは書き換えません）
- **時計 / カレンダー**:
  - **ホバー**: 月間カレンダーをポップアップ表示（ホイールスクロールで前月/翌月送り）
  - **左クリック**: 時間表示と日付表示の切り替え
- **電源（  ）**: 終了・再起動メニューの表示

---

## 新しい環境でのセットアップ手順

### 1. GitとSSHの準備

```bash
sudo pacman -S git openssh

# SSH鍵の生成（既に鍵を持っている場合はスキップ）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 公開鍵を表示してコピーし、GitHubの設定画面に登録してください
cat ~/.ssh/id_ed25519.pub
```

### 2. リポジトリのクローン

```bash
git clone git@github.com:yannsi/esca-dotfiles.git ~/dotfiles
```

### 3. 設定の適用（自動スクリプト）

付属のセットアップスクリプトを実行すると、自動的にシンボリックリンクが作成されます。
`~/dotfiles` 以外の場所に clone した場合も、スクリプトの置き場所を基準にリンクします。
既存の設定は `<名前>.bak.<日時>` に退避されます。

```bash
~/dotfiles/setup.sh
```

### 4. 必要パッケージのインストール

設定を正しく動作させるために、必要なアプリケーションとフォントをインストールします。
すべて公式リポジトリにあるため、AUR ヘルパーは不要です。

```bash
# 共通（Waybar とそのスクリプト、端末、ランチャー、フォント）
sudo pacman -S waybar alacritty fuzzel starship nautilus \
               mpv streamlink cava playerctl brightnessctl wireplumber alsa-utils \
               python python-gobject gtk3 gtk-layer-shell libnotify \
               ttf-hack-nerd ttf-jetbrains-mono noto-fonts-emoji \
               fcitx5-im fcitx5-mozc

# Niri を使う場合
sudo pacman -S niri swaylock swayidle swaybg mako xwayland-satellite polkit-kde-agent

# Hyprland を使う場合
sudo pacman -S hyprland hyprpaper hyprlock hypridle polkit-gnome network-manager-applet \
               grim slurp wl-clipboard xdg-user-dirs
```

インストール後、一度ログアウトして再ログインするか、再起動してください。
