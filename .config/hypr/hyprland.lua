-- ============================================
-- Esca Linux - Hyprland 設定 (Lua)
-- 参考: https://wiki.hypr.land/Configuring/Start/
-- 設定はこのファイルを保存した瞬間に再読み込みされる。
-- 手動で読み直す場合は: hyprctl reload
-- ============================================

------------------
---- モニター ----
------------------
-- 【重要】scale に "auto" を使わないこと。
-- Hyprland の auto は 1.6 のような「論理サイズが整数ピクセルに割り切れない」
-- 倍率を選ぶことがあり、その場合 Hyprland が内部で値を丸める。すると
-- クライアントが想定するサイズと実際の描画サイズがズレて、次が同時に起きる:
--   ・Waybar（レイヤーサーフェス）が想定より大きく描かれる
--   ・ツールチップの座標計算が狂って画面外に出る＝「出ない」ように見える
--   ・fuzzel の --anchor=top-right が効かず、ポップアップが画面中央に出る
-- 実機で3症状が同時に出たため固定値にする。
--
-- 文字が小さすぎる場合は 1.25 / 1.5 / 2 に変える。
-- 1.6 や 1.75 のような値は同じ問題を再発させやすいので避けること。
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = 1,
})

--------------------
---- よく使うもの ----
--------------------
local terminal    = "kitty"
local fileManager = "nautilus"
local menu        = "wofi --show drun"
local mainMod     = "SUPER"

--------------------
---- 見た目 ----
--------------------
hl.config({
    general = {
        gaps_in     = 5,
        gaps_out    = 10,
        border_size = 2,

        col = {
            -- Esca のフィラメントブルー（アンコウの発光をイメージした色）
            active_border   = { colors = { "rgba(1ca2f1ee)", "rgba(3bc7ffee)" }, angle = 45 },
            inactive_border = "rgba(0d1c2eaa)",
        },

        resize_on_border = true,
        allow_tearing    = false,
        layout           = "dwindle",
    },

    decoration = {
        rounding         = 12,
        active_opacity   = 1.0,
        inactive_opacity = 0.93,

        shadow = {
            enabled        = true,
            range          = 14,
            render_power   = 3,
            color          = 0x88000000,
            color_inactive = 0x44000000,
        },

        blur = {
            enabled = true,
            size    = 8,
            passes  = 3,
        },
    },

    animations = {
        enabled = true,
    },

    dwindle = {
        preserve_split = true,
    },

    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        animate_manual_resizes  = true,
        mouse_move_enables_dpms = true,
        key_press_enables_dpms  = true,
    },
})

--------------------
---- アニメーション ----
--------------------
hl.curve("easeOut", { type = "bezier", points = { {0.16, 1},  {0.3,  1}    } })
hl.curve("easeIn",  { type = "bezier", points = { {0.7,  0},  {0.84, 0}    } })
hl.curve("linear",  { type = "bezier", points = { {0, 0},     {1, 1}       } })
hl.curve("easy",    { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.animation({ leaf = "global",     enabled = true, speed = 10,   bezier = "default" })
hl.animation({ leaf = "windows",    enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.49, bezier = "easeIn",  style = "popin 80%" })
hl.animation({ leaf = "border",     enabled = true, speed = 5.39, bezier = "easeOut" })
hl.animation({ leaf = "fade",       enabled = true, speed = 3.03, bezier = "easeOut" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 1.94, bezier = "easeOut", style = "slidevert" })

--------------------
---- キーバインド ----
--------------------
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + C", hl.dsp.window.close())
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))

-- 初心者向け
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + SHIFT + W", hl.dsp.exec_cmd("firefox"))

-- Waybar の表示切り替え
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("pkill waybar || waybar"))

-- フォーカス移動
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- ワークスペース切り替え / ウィンドウ移動
-- hyprlang では9行ほぼ同じ行を並べる必要があったが、Lua ならループで書ける。
for i = 1, 10 do
    local key = i % 10 -- 10 はキー 0 に対応
    hl.bind(mainMod .. " + " .. key,         hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- マウス操作
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + mouse:272",  hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273",  hl.dsp.window.resize(), { mouse = true })

-- 音量・輝度（locked = ロック画面でも有効 / repeating = 長押しで連続）
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true })
hl.bind("XF86AudioMicMute",      hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("brightnessctl set 10%+"),                         { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 10%-"),                         { locked = true, repeating = true })

-- メディアキー（playerctl）
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })

--------------------
---- ウィンドウルール ----
--------------------
hl.window_rule({
    name  = "suppress-maximize-events",
    match = { class = ".*" },
    suppress_event = "maximize",
})

hl.window_rule({
    -- XWayland のドラッグ不具合対策
    name  = "fix-xwayland-drags",
    match = {
        class = "^$", title = "^$",
        xwayland = true, float = true, fullscreen = false, pin = false,
    },
    no_focus = true,
})

--------------------
---- スクリーンショット ----
--------------------
local screenshot = os.getenv("HOME") .. "/.local/bin/screenshot.sh"
hl.bind("Print",         hl.dsp.exec_cmd(screenshot .. " area"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd(screenshot .. " screen"))

--------------------
---- 入力 ----
--------------------
hl.config({
    input = {
        kb_layout    = "jp",
        kb_model     = "jp106",
        follow_mouse = 1,
        sensitivity  = 0,
        touchpad = {
            natural_scroll = false,
        },
    },
})

--------------------
---- 自動起動 ----
--------------------
-- 【重要】ここを消さないこと。この設定を手でコピーしただけの環境でも
-- バー・壁紙・ネットワークアイコンが出るように、単体で完結させてある。
-- インストーラは「まだ書かれていない項目」だけを後から足す作りなので、
-- ここに書いてあるものは二重に起動されない。
--
-- 【重要】waybar は少し待ってから起動する。コンポジタ起動と同時だと
-- pipewire-pulse やシートの初期化が間に合わず、cava モジュールが即死して
-- バーから消えるなどの不安定さが出る。
--
-- 【重要】`sh -c '...'` で包まないこと。
-- 公式の example/hyprland.lua は
--     hl.exec_cmd("waybar & hyprpaper & firefox")
-- のように素のシェル文字列を渡す形しか示していない。exec_cmd 側が既に
-- シェル経由で実行するため、さらに sh -c で包むと引用符が二重になり、
-- Hyprland のコマンド分割で壊れて何も起動しないことがある。
-- && や & といったシェル演算子は、包まずにそのまま書いてよい。
hl.on("hyprland.start", function()
    hl.exec_cmd("sleep 1 && waybar")
    hl.exec_cmd("nm-applet --indicator")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    -- 壁紙。設定は ~/.config/hypr/hyprpaper.conf を参照する。
    hl.exec_cmd("hyprpaper")
end)
