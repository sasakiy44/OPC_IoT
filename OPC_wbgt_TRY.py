from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from aht21 import AHT21
from neopixel import NeoPixel
from time import sleep

# --- 基本設定 ---
BRIGHTNESS = 0.2

# --- 各種モジュールの初期化 ---
i2c = I2C(0) 
oled = SSD1306_I2C(128, 64, i2c)
aht21 = AHT21(i2c)
rgb = NeoPixel(Pin(10, Pin.OUT), 3)

buzzer = PWM(Pin(21))
buzzer.duty_u16(0)

# ==========================================
# ▼ ここから体験授業のハッキングポイント！ ▼
# ==========================================

# 1. アイコンのデザイン（32×32マスの巨大キャンバス！）
# 1マスがより細かくなったので、曲線や複雑な絵も描けます。
# 通常時（アップロードされた画像のデザイン）
ICON_SAFE = [
    "                                ",
    "        #            ##         ",
    "       ###           ##         ",
    "       ###          ###         ",
    "       ####        ## ##        ",
    "       ## ## #######  ##        ",
    "       #################        ",
    "       ####          ####       ",
    "      ##                ###     ",
    "    ##                    ##    ",
    "   ##                      ##   ",
    "  ##       ##      ##       ##  ",
    "  #        ##      ##        #  ",
    " ##                          ## ",
    " #            # #             # ",
    " #         #  ###             # ",
    "##         ## ###  #          ##",
    "##          ### ####          ##",
    "##           #   ##           ##",
    " #           ## ##            # ",
    " #            ###             # ",
    " ##            #             ## ",
    "  #                          #  ",
    "  ##                        ##  ",
    "   ##                      ##   ",
    "    ##                   ###    ",
    "     ###                ###     ",
    "      #####          ######     ",
    "      # ################ ##     ",
    "      ####### #### ## ## #      ",
    "      ##  ##        ## ###      ",
    "                                "
]

# 危険時（暑さで目を細め、舌を出して汗をかいている状態）
ICON_DANGER = [
    "                                ",
    "        #            ##         ",
    "       ###           ##         ",
    "       ###          ###         ",
    "       ####        ## ##        ",
    "       ## ## #######  ##        ",
    "       #################        ",
    "       ####          ####       ",
    "      ##                ###     ",
    "    ##                    ##    ",
    "   ##      # #     # #     ##   ",
    "  ##        #       #       ##  ",
    "  #        # #     # #       #  ",
    " ##                          ## ",
    " #            # #             # ",
    " #         #  ###             # ",
    "##         ## ###  #          ##",
    "##          ### ####          ##",
    "##           #   ##           ##",
    " #                            # ",
    " #                            # ",
    " ##                          ## ",
    "  #                          #  ",
    "  ##                        ##  ",
    "   ##                      ##   ",
    "    ##                   ###    ",
    "     ###                ###     ",
    "      #####          ######     ",
    "      # ################ ##     ",
    "      ####### #### ## ## #      ",
    "      ##  ##        ## ###      ",
    "                                "
]

# 2. アラートのメロディ設定
melody = [
    (1568, 0.20, 0.05), (1397, 0.20, 0.05), (1568, 0.30, 0.30),
    (1568, 0.20, 0.05), (1397, 0.20, 0.05), (1568, 0.30, 0.30),
    (1568, 0.20, 0.05), (1397, 0.20, 0.05), (1568, 0.40, 0.10),
]

# ==========================================

# --- ドット絵を描画する関数 ---
def draw_ascii_icon(oled, icon, x, y, scale=2):
    for row_idx, row in enumerate(icon):
        for col_idx, char in enumerate(row):
            if char != ' ':
                oled.fill_rect(x + col_idx * scale, y + row_idx * scale, scale, scale, 1)

# --- RGB LEDを光らせる関数 ---
def rgb_led(led_no, color, brightness=BRIGHTNESS):
    adjusted_color = tuple(int(c * brightness) for c in color)
    rgb[led_no] = adjusted_color
    rgb.write()

# --- アラート＆フラッシュ演出関数 ---
def warning_action(color):
    duty = 1000 # 音量 (0〜32768)

    for freq, duration, pause in melody:
        if freq > 0 and duty > 0:
            buzzer.freq(freq)
            buzzer.duty_u16(duty)
            for num in range(3): rgb_led(num, color)
            oled.invert(True) 
        
        sleep(duration)
        buzzer.duty_u16(0)
        for num in range(3): rgb_led(num, (0, 0, 0))
        oled.invert(False) 
        sleep(pause)

# --- WBGT値から色(R, G, B)を決定する関数 ---
def get_wbgt_color(wbgt):
    if wbgt < 21:   return (0, 0, 255)
    elif wbgt < 25: return (0, 255, 255)
    elif wbgt < 28: return (255, 255, 0)
    elif wbgt < 31: return (255, 128, 0)
    elif wbgt < 33: return (255, 0, 0)
    else:           return (255, 0, 255)

# ==========================================
# メインプログラム開始
# ==========================================
try:
    while True:
        temp = aht21.temperature
        humi = aht21.relative_humidity
        wbgt = 0.724 * temp + 0.027 * humi + 4.97
        
        oled.fill(0)
        
        # --- 左側：ダッシュボード表示 ---
        # 文字が1倍（8ピクセル）になったため、左側に様々な情報を並べられます
        oled.text("T: {:.1f}".format(temp), 0, 10, 1)
        oled.text("H: {:.1f}".format(humi), 0, 26, 1)
        oled.text("W: {:.1f}".format(wbgt), 0, 42, 1)
        
        # --- 右側：32x32の巨大アイコン表示 ---
        # x=64(画面の真ん中), y=0(一番上)から描画開始
        # scale=2 なので、ちょうど64x64の正方形(画面右半分)に収まります
        if wbgt >= 31:
            draw_ascii_icon(oled, ICON_DANGER, 64, 0, scale=2)
        else:
            draw_ascii_icon(oled, ICON_SAFE, 64, 0, scale=2)
            
        oled.show()

        # --- アラート制御 ---
        color = get_wbgt_color(wbgt)

        if wbgt >= 31:
            warning_action(color)
        else:
            for num in range(3): rgb_led(num, color)
            sleep(1)

except KeyboardInterrupt:
    pass

finally:
    oled.fill(0)
    oled.invert(False)
    oled.show()
    for num in range(3): rgb_led(num, (0, 0, 0), brightness=1.0)
    buzzer.duty_u16(0)
    print("Program stopped.")