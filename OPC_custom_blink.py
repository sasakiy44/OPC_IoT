# 赤色点滅 67行目～72行目をこれで上書きコピーしよう
            if distance < 10:
                for _ in range(5):  # 5回点滅
                    red_led.on()
                    time.sleep(0.1)
                    red_led.off()
                    time.sleep(0.1)
            elif 10 <= distance <= 50:
                yellow_led.on()
            else:
                green_led.on()