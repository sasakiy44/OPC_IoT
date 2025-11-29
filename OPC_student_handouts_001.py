# LED Parking Sensor
# student handout
# version 1.03
# update 2025/08/26

from machine import Pin
import time
import machine

# LED設定
RED_LED = 4
GREEN_LED = 0
YELLOW_LED = 15

red_led = Pin(RED_LED, Pin.OUT)
yellow_led = Pin(YELLOW_LED, Pin.OUT)
green_led = Pin(GREEN_LED, Pin.OUT)

leds = (red_led, green_led, yellow_led)

# センサ設定
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
            return -1
        # 距離を計算：音速は約0.0343 cm/µs、往復なので2で割る
        distance = (duration * 0.0343) / 2
        return distance
    except:
        return -1

# すべてのLEDをオフにする関数
def turn_off_all_leds():
    for led in leds:
        led.off()

# メイン処理
try:
    while True:
        distance = measure_distance()
        if distance < 0:
            print("距離測定エラー")
            turn_off_all_leds()
        else:
            print(f"距離: {distance:.2f} cm")
            
            # すべてのLEDを一旦オフ 
            turn_off_all_leds()
            
            # カスタムここから！閾値を変えてみよう
            if distance < 30:  # <--- 赤色LEDが点灯する距離はここを変える
                red_led.on()  # デフォルト: 点灯
                for _ in range(5): red_led.on(); time.sleep(0.1); red_led.off(); time.sleep(0.1)  # この行のコメントアウトを解除すると点滅に切り替え
            elif 30 <= distance <= 90:  # <--- 黄色LEDと緑色LEDはここを変える
                yellow_led.on()
            else:
                green_led.on()
        time.sleep(0.5)  # <--- 測定間隔を変えてみよう

except KeyboardInterrupt:
    print("すべてのLEDをオフにします")
    turn_off_all_leds()