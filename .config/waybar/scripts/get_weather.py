#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import time
import os
import re

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "weather_location.txt")

# 日本語・略称の正規化マッピング
CITY_MAP = {
    "那覇": "Naha,Japan",
    "naha": "Naha,Japan",
    "沖縄": "Okinawa,Japan",
    "okinawa": "Okinawa,Japan",
    "名護": "Nago,Japan",
    "nago": "Nago,Japan",
    "石垣": "Ishigaki,Japan",
    "ishigaki": "Ishigaki,Japan",
    "宮古島": "Miyakojima,Japan",
    "東京": "Tokyo,Japan",
    "tokyo": "Tokyo,Japan",
    "大阪": "Osaka,Japan",
    "osaka": "Osaka,Japan",
    "京都": "Kyoto,Japan",
    "kyoto": "Kyoto,Japan",
    "名古屋": "Nagoya,Japan",
    "nagoya": "Nagoya,Japan",
    "福岡": "Fukuoka,Japan",
    "fukuoka": "Fukuoka,Japan",
    "札幌": "Sapporo,Japan",
    "sapporo": "Sapporo,Japan",
    "仙台": "Sendai,Japan",
    "sendai": "Sendai,Japan",
    "横浜": "Yokohama,Japan",
    "yokohama": "Yokohama,Japan",
    "広島": "Hiroshima,Japan",
    "hiroshima": "Hiroshima,Japan",
    "神戸": "Kobe,Japan",
    "kobe": "Kobe,Japan",
}

OVERSEAS_CITIES = {
    "new_york", "newyork", "london", "paris", "seoul", "taipei",
    "sydney", "rome", "berlin", "hawaii", "los_angeles", "losangeles",
    "toronto", "vancouver", "singapore", "bangkok", "hong_kong", "hongkong"
}

def resolve_city_query(raw_city):
    raw_lower = raw_city.strip().lower()
    
    # 辞書にあればそれを使用
    if raw_city in CITY_MAP:
        return CITY_MAP[raw_city]
    if raw_lower in CITY_MAP:
        return CITY_MAP[raw_lower]
        
    # すでに国名やカンマが含まれている場合（例: "Naha,Japan", "Paris,France"）
    if "," in raw_city:
        return raw_city.replace(" ", "_")
        
    # 海外主要都市の場合はそのまま
    if raw_lower in OVERSEAS_CITIES:
        return raw_city.replace(" ", "_")
        
    # その他（日本の地名と想定して ,Japan を補完）
    # 日本語文字を含む場合、または単純な英単語の場合
    return f"{raw_city.replace(' ', '_')},Japan"

def get_city():
    try:
        with open(CONFIG_FILE, "r") as f:
            city = f.read().strip()
            if city:
                return city
    except Exception:
        pass
    return "Naha,Japan"

def get_weather():
    raw_city = get_city()
    query_city = resolve_city_query(raw_city)
    city_encoded = urllib.parse.quote(query_city)
    
    # format=1: 天気アイコン + 気温 (例: 🌤️ +29°C)
    text_url = f"https://wttr.in/{city_encoded}?format=1"
    # format=4: 地名 + 天気 + 気温 + 風速
    tooltip_url = f"https://wttr.in/{city_encoded}?format=4"

    max_retries = 3
    for _ in range(max_retries):
        try:
            req_text = urllib.request.Request(text_url, headers={"User-Agent": "curl/7.88.1"})
            with urllib.request.urlopen(req_text, timeout=8) as response:
                text = response.read().decode('utf-8').strip()
            
            req_tooltip = urllib.request.Request(tooltip_url, headers={"User-Agent": "curl/7.88.1"})
            with urllib.request.urlopen(req_tooltip, timeout=8) as response:
                tooltip = response.read().decode('utf-8').strip()

            if "Unknown location" in text or "not found" in text or not text:
                pass
            else:
                output = {
                    "text": text,
                    "tooltip": tooltip
                }
                print(json.dumps(output, ensure_ascii=False))
                return

        except Exception:
            time.sleep(1)
            continue
    
    print(json.dumps({"text": "...", "tooltip": "天気情報の取得に失敗しました"}, ensure_ascii=False))

if __name__ == "__main__":
    get_weather()
