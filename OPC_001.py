# LED Parking Sensor
# Jul. 23 2025  

from machine import Pin
import time
import machine  # time_pulse_us のためにインポート

# LEDピンの設定: 赤 4, 緑 0, 黄 15
RED_LED = 4
GREEN_LED = 0
YELLOW_LED = 15

red_led = Pin(RED_LED, Pin.OUT)
yellow_led = Pin(YELLOW_LED, Pin.OUT)
green_led = Pin(GREEN_LED, Pin.OUT)

leds = (red_led, green_led, yellow_led)

# 超音波センサのピンの設定
TRIG_PIN = 5
ECHO_PIN = 18

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

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
            return -1  # エラーまたはタイムアウト
        
        # 距離を計算：音速は約0.0343 cm/µs、往復なので2で割る
        distance = (duration * 0.0343) / 2
        return distance
    except:
        return -1  # エラー時のフォールバック

# すべてのLEDをオフにする関数
def turn_off_all_leds():
    for led in leds:
        led.off()

# メインループ
try:
    while True:
        distance = measure_distance()
        
        if distance < 0:
            print("距離測定エラー")
            turn_off_all_leds()
        else:
            # 距離に応じてメッセージを変化
            print(f"距離: {distance:.2f} cm - {'近すぎるよ！' if distance < 30 else 'ちょうどいい' if distance <= 60 else '遠いね'}")
            
            # すべてのLEDを一旦オフ
            turn_off_all_leds()
            
            # 距離に応じてLEDを点灯
            # （必要に応じて閾値を調整）
            if distance < 30:
                for _ in range(5):  # 5回点滅
                    red_led.on()
                    time.sleep(0.1)
                    red_led.off()
                    time.sleep(0.1)
            elif 30 <= distance <= 60:
                yellow_led.on()
            else:
                green_led.on()
        
        # 測定間隔（0.5秒、必要に応じて調整）
        time.sleep(0.5)

# CTRL-Cが押されたらすべてのLEDをオフ
except KeyboardInterrupt:
    print("すべてのLEDをオフにします")
    turn_off_all_leds()