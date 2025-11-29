# LED Parking Sensor for ESP32-C3M-TRY
# version 1.05a
# update 2025/11/29

from machine import Pin, I2C
import time
import machine
from neopixel import NeoPixel
from ssd1306 import SSD1306_I2C

# カラーLED設定 (RGB LED on GPIO10, 3 LEDs)
RGB_LED_PIN = 10
rgb = NeoPixel(Pin(RGB_LED_PIN, Pin.OUT), 3)

# 輝度設定（0.0から1.0の範囲で調整可能、デフォルト1.0）
BRIGHTNESS = 0.2  # <--- ここを変えて輝度を調整（例: 0.2で低輝度、1.0でフル輝度）

# センサ設定
TRIG_PIN = 4
ECHO_PIN = 5
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# OLED設定
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
X_OFFSET = 30  # 0.42インチOLEDの有効領域（72x40）の中央寄せ
Y_OFFSET = 12

# 距離を測定する関数（単位：cm）
def measure_distance():
    # トリガーピンを初期化
    trig.off()
    time.sleep_us(2)
    
    # トリガーパルスを送信（10マイクロ秒）
    trig.on()
    time.sleep_us(10)
    trig.off()
    try:
        # エコーパルスの持続時間を測定（タイムアウトは30ms）
        duration = machine.time_pulse_us(echo, 1, 30000)
        if duration < 0:
            return -1
        # 距離を計算：音速は約0.0343 cm/µs、往復なので2で割る
        distance = (duration * 0.0343) / 2
        return distance
    except:
        return -1

# LEDをオフにする関数
def turn_off_all_leds():
    for i in range(3):
        rgb[i] = (0, 0, 0)
    rgb.write()

# LEDの色を設定する関数（輝度調整付き）
def set_led_color(color):
    r, g, b = color
    adjusted_color = (int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))
    for i in range(3):
        rgb[i] = adjusted_color
    rgb.write()

# 赤色点滅関数（輝度調整付き）
def blink_red(times=5, delay=0.1):
    red_color = (255, 0, 0)
    off_color = (0, 0, 0)
    for _ in range(times):
        set_led_color(red_color)  # 輝度調整付きでオン
        time.sleep(delay)
        set_led_color(off_color)  # オフ
        time.sleep(delay)

# パーキングセンサー風のバーを描画する関数（距離が近いほど多くのバーが点灯）
def draw_parking_bars(distance):
    # 最大バー数: 5
    max_bars = 5
    # バー数を決定: 距離が近いほど多くのバー (例: <10cm=5, >50cm=1)
    if distance < 10:
        bars = max_bars
    elif 10 <= distance <= 50:
        bars = 3
    else:
        bars = 1
    
    # バー描画位置（横並び、左から点灯、もっと下に移動）
    base_y = 50  # <--- 下に移動
    bar_height = 20  # サイズを大きく
    bar_width = 10   # サイズを大きく
    bar_spacing = 3
    start_x = 35  # 中央寄せ調整
    
    for i in range(bars):  # 点灯バーだけ描画（消灯時は何も描画しない）
        x = start_x + i * (bar_width + bar_spacing)
        oled.fill_rect(x, base_y - bar_height, bar_width, bar_height, 1)  # 塗りつぶしバーで強調

# 距離を表示する関数（OLEDに表示、テキスト + パーキングバーグラフィック）
def display_distance(distance):
    if distance < 30:
        message = "近いよ"
    elif 30 <= distance <= 90:
        message = "ちょうどいい"
    else:
        message = "遠いね"
    
    # コンソール出力（デバッグ用）
    print(f"距離: {distance:.2f} cm - {message}")
    
    # OLED表示（オフセット適用、画面クリア）
    oled.fill(0)
    oled.text(f"Dist: {int(distance)}cm", X_OFFSET, Y_OFFSET, 1)  # 距離（整数で簡略）
    draw_parking_bars(distance)  # パーキングセンサー風バーグラフィックを追加
    oled.show()

# メイン処理
try:
    oled.fill(0)  # 起動時にOLEDクリア
    oled.show()
    while True:
        distance = measure_distance()
        if distance < 0:
            print("距離測定エラー")
            turn_off_all_leds()
            oled.fill(0)
            oled.text("Error", X_OFFSET, Y_OFFSET + 20, 1)
            oled.show()
        else:
            display_distance(distance)
            
            # LEDを一旦オフ 
            turn_off_all_leds()
            
            # カスタムここから！閾値を変えてみよう
            if distance < 30:  # <--- 赤色LEDが点灯する距離はここを変える
                # デフォルト: 点灯
                set_led_color((255, 0, 0))  # 輝度調整付き赤点灯
                # 点滅を有効にするには以下の行のコメントアウトを解除
                #blink_red()  # 赤色点滅を呼び出す
            elif 30 <= distance <= 90:  # <--- 黄色LEDと緑色LEDはここを変える
                set_led_color((255, 255, 0))  # 黄
            else:
                set_led_color((0, 255, 0))  # 緑
        time.sleep(0.5)  # <--- 測定間隔を変えてみよう

except KeyboardInterrupt:
    print("LEDをオフにします")
    turn_off_all_leds()
    oled.fill(0)
    oled.show()
