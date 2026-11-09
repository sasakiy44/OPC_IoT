# メッセージのカスタマイズ 110行目～116行目をこれで上書きコピーしよう
def display_distance(distance):
    if distance < 30:
        message = "近いよ"
    elif 30 <= distance <= 90:
        message = "ちょうどいい"
    else:
        message = "遠いね"