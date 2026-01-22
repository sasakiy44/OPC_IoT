# welcome.py

from machine import Pin, I2C
from neopixel import NeoPixel
from oledjp import OLEDJP_I2C
import time

# NeoPixel設定
PIN_NUM = 10
NUM_LEDS = 3
BRIGHTNESS = 30 # LEDの明るさ (0-255)

# OLED設定
i2c = I2C(0)

# タイミング設定
LED_ROTATION_INTERVAL = 500  # LEDの色が切り替わる間隔 (ミリ秒)
SCROLL_INTERVAL = 300        # テキストが1文字スクロールする間隔 (ミリ秒)

# デバイスの初期化
# NeoPixel
rgb = NeoPixel(Pin(PIN_NUM, Pin.OUT), NUM_LEDS)
# OLED
oled = OLEDJP_I2C(128, 64, i2c)

# 色の定義
RED = (BRIGHTNESS, 0, 0)
GREEN = (0, BRIGHTNESS, 0)
BLUE = (0, 0, BRIGHTNESS)
OFF = (0, 0, 0)

# LEDのカラーパターン
color_patterns = [
    (RED, GREEN, BLUE),
    (GREEN, BLUE, RED),
    (BLUE, RED, GREEN)
]

# OLEDスクロールテキストの準備
oled.setFont(OLEDJP_I2C.MISAKI)
oled.setFontSize(2)
text_to_scroll = "神戸電子専門学校にようこそ"
screen_width_chars = 8
padding = " " * screen_width_chars
scroll_buffer = padding + text_to_scroll + padding

# メイン処理
print("プログラムを開始します。停止するには Ctrl+C を押してください。")

try:
    # 状態変数の初期化
    last_led_update = time.ticks_ms()
    last_scroll_update = time.ticks_ms()
    led_pattern_index = 0
    scroll_position = 0

    # 無限ループで動作を繰り返す
    while True:
        now = time.ticks_ms()

        # LEDのカラーローテーション処理
        if time.ticks_diff(now, last_led_update) >= LED_ROTATION_INTERVAL:
            last_led_update = now
            
            # 現在のパターンでLEDを点灯
            current_pattern = color_patterns[led_pattern_index]
            rgb[0] = current_pattern[0]
            rgb[1] = current_pattern[1]
            rgb[2] = current_pattern[2]
            rgb.write()
            
            # 次のパターンへ
            led_pattern_index = (led_pattern_index + 1) % len(color_patterns)

        # OLEDのスクロール処理
        if time.ticks_diff(now, last_scroll_update) >= SCROLL_INTERVAL:
            last_scroll_update = now
            
            # 表示するテキストのスライスを決定
            display_text = scroll_buffer[scroll_position : scroll_position + screen_width_chars]
            
            # OLEDをクリアしてテキストを表示
            oled.clear()
            oled.println(display_text)
            
            # スクロール位置を更新
            scroll_position += 1
            if scroll_position >= len(scroll_buffer) - screen_width_chars:
                scroll_position = 0 # テキストの最後までスクロールしたら最初に戻る
        
        # CPUの過剰な使用を防ぐための短い待機
        time.sleep_ms(10)

except KeyboardInterrupt:
    # プログラムが停止された（Ctrl+Cが押された）場合の処理
    print("プログラムを停止します。")

finally:
    # 最後に必ず全てのLEDを消灯させ、OLEDをクリアする
    for i in range(NUM_LEDS):
        rgb[i] = OFF
    rgb.write()
    oled.clear()
