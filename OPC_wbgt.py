# WBGT monitor for ESP32-C3M-TRY
# student handout
# version 1.00
# update 2026/07/28

from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from aht21 import AHT21
from neopixel import NeoPixel
from time import sleep

# --- RGB LED輝度設定 ---
BRIGHTNESS = 0.3

# --- 各種モジュールの初期化 ---
i2c = I2C(0) 
oled = SSD1306_I2C(128, 64, i2c)
aht21 = AHT21(i2c)
rgb = NeoPixel(Pin(10, Pin.OUT), 3)

buzzer = PWM(Pin(21))
buzzer.duty_u16(0) # 最初は音を止めておく

# RGB LEDを光らせる関数
def rgb_led(led_no, color, brightness=BRIGHTNESS):
    adjusted_color = tuple(int(c * brightness) for c in color)
    rgb[led_no] = adjusted_color
    rgb.write()

# ポテト風メロディ＆LED同期アラート
# 「ソ・ファ・ソ」のメロディ (周波数, 鳴らす秒数, 休む秒数)
melody = [
    # 1回目
    (1568, 0.20, 0.05),  # ソ
    (1397, 0.20, 0.05),  # ファ
    (1568, 0.30, 0.30),  # ソ（長め）
    # 2回目
    (1568, 0.20, 0.05),
    (1397, 0.20, 0.05),
    (1568, 0.30, 0.30),
    # 3回目
    (1568, 0.20, 0.05),
    (1397, 0.20, 0.05),
    (1568, 0.40, 0.10),
]

def warning_action(color):
    # 0:消音, 1:小, 2:中, 3:最大
    volume_level = 2
    
    if volume_level == 3: duty = 32768
    elif volume_level == 2: duty = 5000
    elif volume_level == 1: duty = 1200
    else: duty = 0

    # メロディの配列を順番に読み込んで再生
    for freq, duration, pause in melody:
        if freq > 0 and duty > 0:
            # 音を鳴らす ＆ LEDを光らせる（音と光の同期！）
            buzzer.freq(freq)
            buzzer.duty_u16(duty)
            for num in range(3): rgb_led(num, color)
        
        sleep(duration) # 鳴らす時間待機
        
        # 音を止める ＆ LEDを消す
        buzzer.duty_u16(0)
        for num in range(3): rgb_led(num, (0, 0, 0))
        
        sleep(pause) # 次の音までのすきま待機

# 7セグメント描画用の関数
def draw_7seg_char(oled, char, x, y, w, h, t):
    segs = {
        '0': (1,1,1,1,1,1,0), '1': (0,1,1,0,0,0,0), '2': (1,1,0,1,1,0,1),
        '3': (1,1,1,1,0,0,1), '4': (0,1,1,0,0,1,1), '5': (1,0,1,1,0,1,1),
        '6': (1,0,1,1,1,1,1), '7': (1,1,1,0,0,0,0), '8': (1,1,1,1,1,1,1),
        '9': (1,1,1,1,0,1,1), ' ': (0,0,0,0,0,0,0), '-': (0,0,0,0,0,0,1)
    }
    if char not in segs: return
    s = segs[char]
    if s[0]: oled.fill_rect(x + t + 1, y, w - 2*t - 2, t, 1) # A
    if s[1]: oled.fill_rect(x + w - t, y + t + 1, t, h//2 - t - 1, 1) # B
    if s[2]: oled.fill_rect(x + w - t, y + h//2 + 1, t, h//2 - t - 1, 1) # C
    if s[3]: oled.fill_rect(x + t + 1, y + h - t, w - 2*t - 2, t, 1) # D
    if s[4]: oled.fill_rect(x, y + h//2 + 1, t, h//2 - t - 1, 1) # E
    if s[5]: oled.fill_rect(x, y + t + 1, t, h//2 - t - 1, 1) # F
    if s[6]: oled.fill_rect(x + t + 1, y + h//2 - t//2, w - 2*t - 2, t, 1) # G

def draw_7seg_str(oled, text, x, y, w, h, t):
    curr_x = x
    for char in text:
        if char == '.':
            oled.fill_rect(curr_x, y + h - t, t, t, 1)
            curr_x += t + 4
        else:
            draw_7seg_char(oled, char, curr_x, y, w, h, t)
            curr_x += w + 6

# WBGT値から色(R, G, B)を決定する関数
def get_wbgt_color(wbgt):
    if wbgt < 21:   return (0, 0, 255)       # 青
    elif wbgt < 25: return (0, 255, 255)     # 水色
    elif wbgt < 28: return (255, 255, 0)     # 黄
    elif wbgt < 31: return (255, 128, 0)     # 橙
    elif wbgt < 33: return (255, 0, 0)       # 赤
    else:           return (255, 0, 255)     # 紫


# メインプログラム
try:
    while True:
        # 1. 温度・湿度の取得と計算
        temp = aht21.temperature
        humi = aht21.relative_humidity
        wbgt = 0.724 * temp + 0.027 * humi + 4.97
        
        # 2. 画面の更新
        oled.fill(0)
        temp_str = "{:.1f}".format(temp)
        draw_7seg_str(oled, temp_str, 4, 4, 30, 56, 6)
        oled.show()

        # 3. 色の判定
        color = get_wbgt_color(wbgt)

        # 4. LEDと音の制御
        if wbgt >= 31:
            # 【初期状態】ただ赤く光るだけ
            for num in range(3): rgb_led(num, color)
            sleep(1)
            
            # --------------------------------------------------
            # ▼ ミッション：危険なときにアラートを鳴らそう！ ▼
            # --------------------------------------------------
            # プログラミングでは「#」の後の文字は無視されます（コメントアウト）。
            # すぐ上の2行（for... と sleep...）の先頭に「#」を付けて動かないようにして、
            # 下の「warning_action(color)」の先頭の「#」を消してみてください！
            
            #warning_action(color)
            
        else:
            # 31℃未満（安全）のときは通常通り常時点灯
            for num in range(3): rgb_led(num, color)
            sleep(1)

except KeyboardInterrupt:
    pass

finally:
    # 終了時に確実にお片付け
    oled.fill(0)
    oled.show()
    for num in range(3):
        rgb_led(num, (0, 0, 0), brightness=1.0)
    buzzer.duty_u16(0)
    print("Program stopped.")
