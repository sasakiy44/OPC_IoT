# ブザー音のカスタマイズ 78行目～84行目をこれで上書きコピーしよう
def beep_buzzer():
    buzzer = machine.PWM(machine.Pin(21))
    buzzer.freq(2500)  # 2500Hzの高めの音
    for _ in range(3): # 3回繰り返す
        buzzer.duty(512)
        time.sleep(0.05) # 0.05秒鳴らす
        buzzer.duty(0)
        time.sleep(0.05) # 0.05秒休む
    buzzer.deinit()
