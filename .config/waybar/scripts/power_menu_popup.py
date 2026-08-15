#!/usr/bin/env python3
"""
Waybar Power Menu Popup using GTK3 and gtk-layer-shell
"""
import sys
import os
import subprocess
import signal

PID_FILE = "/tmp/waybar_power_menu_popup.pid"

# トグル動作: 既に起動している場合は終了
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, "r") as f:
            old_pid = int(f.read().strip())
        os.kill(old_pid, signal.SIGTERM)
        os.remove(PID_FILE)
        sys.exit(0)
    except Exception:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

try:
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
except Exception:
    pass

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib

CSS_STYLE = """
/* ウィンドウ自体は完全に透明（四隅のアーティファクト防止） */
window {
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
}

/* メインコンテナ（背景・角丸・枠線） */
.main-container {
    background-color: #1e1e2e;
    border: 1px solid rgba(137, 180, 250, 0.45);
    border-radius: 12px;
    padding: 10px 12px 10px 12px;
}

/* ヘッダータイトル */
.header-title {
    color: #cba6f7;
    font-family: "JetBrains Mono", "Hack Nerd Font", "Noto Sans CJK JP", sans-serif;
    font-size: 13px;
    font-weight: bold;
    padding: 2px 4px 6px 4px;
}

/* ボタン共通リセット & スタイル */
button {
    all: unset;
    background-image: none;
    box-shadow: none;
    text-shadow: none;
    border: none;
    outline: none;
}

.power-btn {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 9px 14px;
    margin: 3px 0px;
    color: #cdd6f4;
}

.power-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.25);
}

.btn-icon {
    font-family: "Hack Nerd Font", monospace;
    font-size: 16px;
}

.btn-label {
    font-family: "JetBrains Mono", "Hack Nerd Font", "Noto Sans CJK JP", sans-serif;
    font-size: 13px;
    font-weight: bold;
    color: #cdd6f4;
}

/* 各アクション固有のカラー */
/* 1. シャットダウン */
.btn-shutdown {
    border-left: 3px solid #f38ba8;
}
.btn-shutdown .btn-icon {
    color: #f38ba8;
}
.btn-shutdown:hover {
    background-color: rgba(243, 139, 168, 0.22);
    border-color: #f38ba8;
}

/* 2. 再起動 */
.btn-reboot {
    border-left: 3px solid #fab387;
}
.btn-reboot .btn-icon {
    color: #fab387;
}
.btn-reboot:hover {
    background-color: rgba(250, 179, 135, 0.22);
    border-color: #fab387;
}

/* 3. サスペンド */
.btn-suspend {
    border-left: 3px solid #89b4fa;
}
.btn-suspend .btn-icon {
    color: #89b4fa;
}
.btn-suspend:hover {
    background-color: rgba(137, 180, 250, 0.22);
    border-color: #89b4fa;
}

/* 4. 画面ロック */
.btn-lock {
    border-left: 3px solid #a6e3a1;
}
.btn-lock .btn-icon {
    color: #a6e3a1;
}
.btn-lock:hover {
    background-color: rgba(166, 227, 161, 0.22);
    border-color: #a6e3a1;
}

/* 5. ログアウト */
.btn-logout {
    border-left: 3px solid #cba6f7;
}
.btn-logout .btn-icon {
    color: #cba6f7;
}
.btn-logout:hover {
    background-color: rgba(203, 166, 247, 0.22);
    border-color: #cba6f7;
}

/* キャンセルボタン */
.btn-cancel {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 7px 14px;
    margin-top: 3px;
    margin-bottom: 2px;
}
.btn-cancel .btn-icon {
    color: #a6adc8;
}
.btn-cancel .btn-label {
    color: #a6adc8;
    font-weight: normal;
}
.btn-cancel:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.12);
}
.btn-cancel:hover .btn-label {
    color: #ffffff;
}

separator {
    background-color: rgba(255, 255, 255, 0.1);
    min-height: 1px;
    margin: 4px 0px;
}
"""

def detect_wm():
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "hyprland" in desktop:
        return "hyprland"
    if "niri" in desktop:
        return "niri"
    if os.environ.get("NIRI_SOCKET"):
        return "niri"
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "hyprland"
    return "unknown"

def lock_screen():
    wm = detect_wm()
    if wm == "hyprland" and subprocess.call(["command", "-v", "hyprlock"], shell=True, stdout=subprocess.DEVNULL) == 0:
        subprocess.Popen(["hyprlock"])
    elif subprocess.call(["command", "-v", "swaylock"], shell=True, stdout=subprocess.DEVNULL) == 0:
        subprocess.Popen(["swaylock", "-f"])
    else:
        subprocess.Popen(["swaylock"])

def logout_session():
    wm = detect_wm()
    if wm == "hyprland":
        subprocess.Popen(["hyprctl", "dispatch", "exit"])
    elif wm == "niri":
        subprocess.Popen(["niri", "msg", "action", "quit", "-s"])
    else:
        user = os.environ.get("USER", "")
        subprocess.Popen(["loginctl", "terminate-user", user])

class PowerMenuPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        
        # ウィンドウのRGBA透過設定（角丸の外側の不要なアーティファクト・角を完全に除去）
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Layer Shell 設定
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 38)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 8)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_title("Power Menu")
        self.set_resizable(False)
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        # メインコンテナ（Boxに .main-container を設定して角丸・背景を描画）
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        main_box.get_style_context().add_class("main-container")
        self.add(main_box)

        # ヘッダー
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_label = Gtk.Label(label="⏻  電源メニュー")
        title_label.get_style_context().add_class("header-title")
        header_box.pack_start(title_label, True, True, 0)
        main_box.pack_start(header_box, False, False, 0)

        # アクションボタンの定義
        actions = [
            ("", "シャットダウン", "btn-shutdown", self.action_shutdown),
            ("", "再起動", "btn-reboot", self.action_reboot),
            ("", "サスペンド", "btn-suspend", self.action_suspend),
            ("", "画面ロック", "btn-lock", self.action_lock),
            ("󰗼", "ログアウト", "btn-logout", self.action_logout),
        ]

        for icon, label_text, style_class, callback in actions:
            btn = self.create_button(icon, label_text, style_class, callback)
            main_box.pack_start(btn, False, False, 0)

        # セパレーター
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(sep, False, False, 2)

        # キャンセルボタン
        cancel_btn = self.create_button("󰅖", "キャンセル", "btn-cancel", self.action_cancel)
        main_box.pack_start(cancel_btn, False, False, 0)

    def create_button(self, icon_str, text_str, style_class, callback):
        btn = Gtk.Button()
        btn.get_style_context().add_class("power-btn")
        btn.get_style_context().add_class(style_class)
        btn.connect("clicked", callback)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        icon = Gtk.Label(label=icon_str)
        icon.get_style_context().add_class("btn-icon")
        icon.set_xalign(0.5)
        icon.set_width_chars(2)

        label = Gtk.Label(label=text_str)
        label.get_style_context().add_class("btn-label")
        label.set_xalign(0.0)

        box.pack_start(icon, False, False, 0)
        box.pack_start(label, True, True, 0)
        btn.add(box)
        return btn

    def action_shutdown(self, widget):
        self.cleanup_and_quit()
        subprocess.Popen(["systemctl", "poweroff"])

    def action_reboot(self, widget):
        self.cleanup_and_quit()
        subprocess.Popen(["systemctl", "reboot"])

    def action_suspend(self, widget):
        self.cleanup_and_quit()
        subprocess.Popen(["systemctl", "suspend"])

    def action_lock(self, widget):
        self.cleanup_and_quit()
        lock_screen()

    def action_logout(self, widget):
        self.cleanup_and_quit()
        logout_session()

    def action_cancel(self, widget):
        self.cleanup_and_quit()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.cleanup_and_quit()
            return True
        return False

    def on_focus_out(self, widget, event):
        self.cleanup_and_quit()
        return True

    def cleanup_and_quit(self):
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass
        Gtk.main_quit()

    def on_destroy(self, widget):
        self.cleanup_and_quit()

def main():
    # CSS プロバイダー設定
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS_STYLE.encode('utf-8'))
    Gtk.StyleContext.add_provider_for_screen(
        screen,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = PowerMenuPopup()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
