# esca-dotfiles

Arch Linux + Niri / Hyprland デスクトップ環境の設定ファイル集です。
統一感のあるパステルテーマ（Catppuccin Mocha / Macchiato）および Esca テーマで構成されています。

## 収録されている設定

- **Window Manager**: Niri, Hyprland (`.config/hypr/hyprland.lua`)
- **Status Bar**: Waybar（Fuzzelラジオ、Chrome/Firefoxランチャー、カレンダー、天気予報、CAVAビジュアライザー内蔵）
- **Terminal**: Alacritty
- **Launcher**: Fuzzel
- **Screen Locker / Logout**: Swaylock, wlogout
- **Shell Prompt**: Starship

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

```bash
~/dotfiles/setup.sh
```

### 4. 必要パッケージのインストール

設定を正しく動作させるために、必要なアプリケーションとフォントをインストールします。

```bash
# 必須・基本パッケージ
sudo pacman -S niri waybar alacritty fuzzel swaylock starship \
               mpv cava playerctl brightnessctl wireplumber python

# フォント（アイコン表示に必須）
# AURヘルパー（yayなど）を使用している場合:
yay -S ttf-hack-nerd ttf-jetbrains-mono noto-fonts-emoji
```

インストール後、一度ログアウトして再ログインするか、再起動してください。
