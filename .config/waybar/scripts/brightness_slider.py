#!/usr/bin/env python3
import sys
import os
import subprocess
import signal

# 既に起動している場合は終了（トグル動作）
pid_file = "/tmp/waybar_brightness_slider.pid"
if os.path.exists(pid_file):
    try:
        with open(pid_file, "r") as f:
            old_pid = int(f.read().strip())
        os.kill(old_pid, signal.SIGTERM)
        os.remove(pid_file)
        sys.exit(0)
    except Exception:
        if os.path.exists(pid_file):
            os.remove(pid_file)

with open(pid_file, "w") as f:
    f.write(str(os.getpid()))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

def get_brightness():
    try:
        out = subprocess.check_output(["brightnessctl", "-m"]).decode()
        # 出力フォーマット: intel_backlight,backlight,565,65%,872
        parts = out.strip().split(',')
        if len(parts) >= 4:
            pct_str = parts[3].replace('%', '')
            return int(pct_str)
    except Exception:
        pass
    return 50

def set_brightness(val):
    try:
        # 完全な暗転を防ぐため最低1%に制限
        val = max(1, min(100, int(val)))
        subprocess.run(["brightnessctl", "set", f"{val}%"], stdout=subprocess.DEVNULL)
    except Exception:
        pass

class BrightnessPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        
        # Layer shell 設定
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 38)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 90) # 明るさアイコンの位置付近
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_title("Brightness Slider")
        self.set_default_size(200, 36)
        self.set_resizable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_start(14)
        box.set_margin_end(14)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        self.add(box)

        # アイコン
        self.icon_label = Gtk.Label(label="󰃠")
        box.pack_start(self.icon_label, False, False, 0)

        # スライダー
        cur_val = get_brightness()
        self.update_icon(cur_val)
        self.adjustment = Gtk.Adjustment(value=cur_val, lower=1, upper=100, step_increment=1, page_increment=5)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adjustment)
        self.scale.set_hexpand(True)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_digits(0)
        self.scale.connect("value-changed", self.on_value_changed)
        box.pack_start(self.scale, True, True, 0)

        # CSS Styling (Catppuccin Yellow / Mocha)
        css = b"""
        window {
            background-color: rgba(30, 30, 46, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        }
        label {
            color: #f9e2af;
            font-family: "Hack Nerd Font", sans-serif;
            font-size: 16px;
        }
        scale trough {
            background-color: #313244;
            border-radius: 6px;
            min-height: 8px;
            min-width: 140px;
        }
        scale highlight {
            background-color: #f9e2af;
            border-radius: 6px;
            min-height: 8px;
        }
        scale slider {
            background-color: #cdd6f4;
            border-radius: 50%;
            min-width: 16px;
            min-height: 16px;
            margin: -4px;
        }
        scale slider:hover {
            background-color: #ffffff;
        }
        scale value {
            color: #cdd6f4;
            font-family: "JetBrains Mono", sans-serif;
            font-size: 12px;
            font-weight: bold;
            padding-left: 6px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)

    def update_icon(self, val):
        if val < 33:
            self.icon_label.set_text("󰃞")
        elif val < 66:
            self.icon_label.set_text("󰃟")
        else:
            self.icon_label.set_text("󰃠")

    def on_value_changed(self, scale):
        val = int(scale.get_value())
        set_brightness(val)
        self.update_icon(val)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def on_destroy(self, widget):
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except Exception:
                pass
        Gtk.main_quit()

if __name__ == "__main__":
    win = BrightnessPopup()
    win.show_all()
    Gtk.main()
