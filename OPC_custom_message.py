# メッセージのカスタマイズ 61行目をこれで上書きコピーしよう
            print(f"距離: {distance:.2f} cm - {'近すぎるよ！' if distance < 10 else 'ちょうどいい' if distance <= 50 else '遠いね'}")
