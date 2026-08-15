#!/usr/bin/env python3
import sys
import os
import signal
import datetime
import calendar

# 日本の週始まり（日曜日）に設定
calendar.setfirstweekday(calendar.SUNDAY)

mode = "year" if "--year" in sys.argv or "-y" in sys.argv else "month"

# PIDファイルの管理（トグル動作 & モード切り替え対応）
pid_file = "/tmp/waybar_calendar_popup.pid"
mode_file = "/tmp/waybar_calendar_mode.txt"

if os.path.exists(pid_file):
    try:
        with open(pid_file, "r") as f:
            old_pid = int(f.read().strip())
        old_mode = ""
        if os.path.exists(mode_file):
            with open(mode_file, "r") as f:
                old_mode = f.read().strip()

        # 同じモードが既に起動中なら閉じる（トグル）
        if old_mode == mode:
            os.kill(old_pid, signal.SIGTERM)
            if os.path.exists(pid_file):
                os.remove(pid_file)
            if os.path.exists(mode_file):
                os.remove(mode_file)
            sys.exit(0)
        else:
            # 異なるモードなら既存のプロセスを終了して新規起動
            os.kill(old_pid, signal.SIGTERM)
    except Exception:
        pass

try:
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    with open(mode_file, "w") as f:
        f.write(mode)
except Exception:
    pass

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib

CSS_STYLE = """
window {
    background-color: rgba(30, 30, 46, 0.96);
    border: 1px solid rgba(137, 180, 250, 0.4);
    border-radius: 14px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
}
.cal-icon {
    color: #f5c2e7;
    font-family: "Hack Nerd Font", sans-serif;
    font-size: 16px;
}
.cal-header {
    color: #cdd6f4;
    font-family: "JetBrains Mono", "Hack Nerd Font", sans-serif;
    font-size: 14px;
    font-weight: bold;
}
.nav-btn {
    background-color: rgba(255, 255, 255, 0.06);
    color: #89b4fa;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 2px 8px;
    font-family: "JetBrains Mono", "Hack Nerd Font", sans-serif;
    font-size: 12px;
    font-weight: bold;
}
.nav-btn:hover {
    background-color: rgba(137, 180, 250, 0.2);
    color: #ffffff;
}
.close-btn {
    color: #f38ba8;
}
.close-btn:hover {
    background-color: rgba(243, 139, 168, 0.2);
    color: #ffffff;
}

/* 月間カレンダーウィジェット */
calendar {
    background-color: #181825;
    color: #cdd6f4;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    font-family: "JetBrains Mono", "Hack Nerd Font", monospace;
    font-size: 13px;
    padding: 6px;
}
calendar:selected {
    background-color: #f5c2e7;
    color: #11111b;
    border-radius: 6px;
    font-weight: bold;
}
calendar.header {
    color: #cba6f7;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
calendar.button {
    color: #89b4fa;
    background: transparent;
    border: none;
    border-radius: 4px;
}
calendar.button:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
}
calendar.highlight {
    color: #f38ba8;
    font-weight: bold;
}

/* 年間カレンダーウィジェット */
.year-title {
    color: #cba6f7;
    font-family: "JetBrains Mono", "Hack Nerd Font", sans-serif;
    font-size: 16px;
    font-weight: 800;
}
.month-box {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 6px;
}
.month-box-current {
    border: 1px solid rgba(245, 194, 231, 0.5);
    background-color: rgba(24, 24, 37, 0.9);
}
.month-label {
    color: #89b4fa;
    font-family: "JetBrains Mono", "Hack Nerd Font", sans-serif;
    font-size: 12px;
    font-weight: bold;
    margin-bottom: 2px;
}
.month-label-current {
    color: #f5c2e7;
}
.weekday-header {
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: bold;
    margin-bottom: 2px;
}
.day-sun { color: #f38ba8; }
.day-sat { color: #89b4fa; }
.day-normal { color: #a6adc8; }
.day-num {
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    color: #cdd6f4;
    min-width: 18px;
    min-height: 18px;
}
.day-today {
    background-color: #f5c2e7;
    color: #11111b;
    font-weight: bold;
    border-radius: 4px;
}
"""

def get_wareki(year):
    if year >= 2019:
        reiwa = year - 2018
        return f"令和{reiwa if reiwa > 1 else '元'}年"
    elif year >= 1989:
        heisei = year - 1988
        return f"平成{heisei if heisei > 1 else '元'}年"
    return ""

class MonthCalendarPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 38)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 35)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_title("Month Calendar")
        self.set_resizable(False)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        self.add(main_box)

        # ヘッダー
        now = datetime.datetime.now()
        weekdays_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        wareki = get_wareki(now.year)
        wareki_str = f" ({wareki})" if wareki else ""
        date_str = f"{now.year}年{now.month}月{now.day}日{wareki_str} [{weekdays_jp[now.weekday()]}]"
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon_label = Gtk.Label(label="")
        icon_label.get_style_context().add_class("cal-icon")
        header_label = Gtk.Label(label=date_str)
        header_label.get_style_context().add_class("cal-header")
        
        header_box.pack_start(icon_label, False, False, 0)
        header_box.pack_start(header_label, False, False, 0)
        main_box.pack_start(header_box, False, False, 0)

        # カレンダーウィジェット
        self.calendar = Gtk.Calendar()
        self.calendar.set_property("show-heading", True)
        self.calendar.set_property("show-day-names", True)
        self.calendar.set_property("show-week-numbers", True)
        main_box.pack_start(self.calendar, True, True, 0)

        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def on_destroy(self, widget):
        cleanup()
        Gtk.main_quit()


class YearCalendarPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 38)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 20)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        self.set_title("Year Calendar")
        self.set_resizable(False)

        self.today = datetime.date.today()
        self.current_year = self.today.year

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_margin_start(14)
        self.main_box.set_margin_end(14)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.add(self.main_box)

        # トップナビゲーションバー
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        prev_btn = Gtk.Button(label="◀ 前年")
        prev_btn.get_style_context().add_class("nav-btn")
        prev_btn.connect("clicked", self.on_prev_year)
        nav_box.pack_start(prev_btn, False, False, 0)

        self.title_label = Gtk.Label()
        self.title_label.get_style_context().add_class("year-title")
        nav_box.pack_start(self.title_label, True, True, 0)

        today_btn = Gtk.Button(label="今年")
        today_btn.get_style_context().add_class("nav-btn")
        today_btn.connect("clicked", self.on_this_year)
        nav_box.pack_start(today_btn, False, False, 0)

        next_btn = Gtk.Button(label="翌年 ▶")
        next_btn.get_style_context().add_class("nav-btn")
        next_btn.connect("clicked", self.on_next_year)
        nav_box.pack_start(next_btn, False, False, 0)

        close_btn = Gtk.Button(label="✕")
        close_btn.get_style_context().add_class("nav-btn")
        close_btn.get_style_context().add_class("close-btn")
        close_btn.connect("clicked", lambda b: self.close())
        nav_box.pack_start(close_btn, False, False, 0)

        self.main_box.pack_start(nav_box, False, False, 0)

        # 12ヶ月のグリッドコンテナ
        self.grid_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(self.grid_container, True, True, 0)

        self.render_year()

        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", self.on_destroy)

    def on_prev_year(self, btn):
        self.current_year -= 1
        self.render_year()

    def on_next_year(self, btn):
        self.current_year += 1
        self.render_year()

    def on_this_year(self, btn):
        self.current_year = self.today.year
        self.render_year()

    def render_year(self):
        # 既存グリッドをクリア
        for child in self.grid_container.get_children():
            self.grid_container.remove(child)

        # タイトル更新
        wareki = get_wareki(self.current_year)
        wareki_str = f" ({wareki})" if wareki else ""
        self.title_label.set_text(f"{self.current_year}年{wareki_str}")

        # 4列 × 3行のグリッド
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)

        month_names = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        weekdays_header = ["日", "月", "火", "水", "木", "金", "土"]

        for m_idx in range(12):
            month_num = m_idx + 1
            is_current_month = (self.current_year == self.today.year and month_num == self.today.month)

            m_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            m_box.get_style_context().add_class("month-box")
            if is_current_month:
                m_box.get_style_context().add_class("month-box-current")

            # 月名ラベル
            m_label = Gtk.Label(label=month_names[m_idx])
            m_label.get_style_context().add_class("month-label")
            if is_current_month:
                m_label.get_style_context().add_class("month-label-current")
            m_box.pack_start(m_label, False, False, 0)

            # 月グリッド
            m_grid = Gtk.Grid()
            m_grid.set_row_spacing(2)
            m_grid.set_column_spacing(3)

            # 曜日ヘッダー
            for w_idx, w_name in enumerate(weekdays_header):
                w_lbl = Gtk.Label(label=w_name)
                w_lbl.get_style_context().add_class("weekday-header")
                if w_idx == 0:
                    w_lbl.get_style_context().add_class("day-sun")
                elif w_idx == 6:
                    w_lbl.get_style_context().add_class("day-sat")
                else:
                    w_lbl.get_style_context().add_class("day-normal")
                m_grid.attach(w_lbl, w_idx, 0, 1, 1)

            # 日付
            weeks = calendar.monthcalendar(self.current_year, month_num)
            for r_idx, week in enumerate(weeks):
                for c_idx, day in enumerate(week):
                    if day != 0:
                        d_lbl = Gtk.Label(label=str(day))
                        d_lbl.get_style_context().add_class("day-num")
                        
                        is_today = (self.current_year == self.today.year and month_num == self.today.month and day == self.today.day)
                        if is_today:
                            d_lbl.get_style_context().add_class("day-today")
                        elif c_idx == 0:
                            d_lbl.get_style_context().add_class("day-sun")
                        elif c_idx == 6:
                            d_lbl.get_style_context().add_class("day-sat")
                        
                        m_grid.attach(d_lbl, c_idx, r_idx + 1, 1, 1)

            m_box.pack_start(m_grid, True, True, 0)

            col = m_idx % 4
            row = m_idx // 4
            grid.attach(m_box, col, row, 1, 1)

        self.grid_container.pack_start(grid, True, True, 0)
        self.grid_container.show_all()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def on_destroy(self, widget):
        cleanup()
        Gtk.main_quit()

def cleanup():
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception:
            pass
    if os.path.exists(mode_file):
        try:
            os.remove(mode_file)
        except Exception:
            pass

if __name__ == "__main__":
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(CSS_STYLE.encode('utf-8'))
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    if mode == "year":
        win = YearCalendarPopup()
    else:
        win = MonthCalendarPopup()

    win.show_all()
    Gtk.main()
