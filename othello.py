import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont


def create_pic_othello(match, size):
    black = Image.open("./othello/black.png")
    white = Image.open("./othello/white.png")
    can = Image.open("./othello/can.png")
    null = Image.open("./othello/null.png")
    othello = Image.new(mode="RGB", size=(size*50, size*50), color=0xffffff)
    i = 0
    moji = ImageDraw.Draw(othello)
    for line in match[1:size+1]:
        j = 0
        for cell in line[1:size+1]:
            if cell == 1:
                othello.paste(black, (i, j))
            elif cell == 2:
                othello.paste(white, (i, j))
            elif cell == 3:
                othello.paste(can, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            else:
                othello.paste(null, (i, j))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((i+9, j+9), text=f"{int(i/50+1)}{int(j/50+1)}", font=font, fill=0x000000)
            j += 50
        i += 50
    othello.save("./game_pic/othello.png")


async def match_othello(client3, message, about_othello):
    size = about_othello[1]
    match = [[0] * (size+2) for i in range(size+2)]
    match[int(size/2)][int(size/2)] = 2
    match[int(size/2+1)][int(size/2+1)] = 2
    match[int(size/2+1)][int(size/2)] = 1
    match[int(size/2)][int(size/2+1)] = 1
    match[int(size/2-1)][int(size/2)] = 3
    match[int(size/2)][int(size/2-1)] = 3
    match[int(size/2+1)][int(size/2+2)] = 3
    match[int(size/2+2)][int(size/2+1)] = 3

    temp = random.choice((2, 3))
    sente = about_othello[temp]
    gote = about_othello[5-temp]
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)

    def msg_check(m):
        return m.channel == message.channel and not m.author.bot

    n = 0
    while True:
        index = n % 2
        teban_member = player_list[index]
        create_pic_othello(match, size)
        f = discord.File("./game_pic/othello.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)

        is_exist_can_put_place = False
        for line in match[1:size+1]:
            for cell in line[1:size+1]:
                if cell == 3:
                    is_exist_can_put_place = True
                    break
            if is_exist_can_put_place:
                break

        if is_exist_can_put_place: #置ける場所があるなら
            series_pass = False

            while True:
                timeout = False
                for remain_time in (50, 10):
                    try:
                        reply = await client3.wait_for("message", check=msg_check, timeout=remain_time)
                    except asyncio.TimeoutError:
                        if remain_time == 10:
                            next_index = (n+1)%2
                            await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                            timeout = True
                            break
                        else:
                            await message.channel.send("残り10秒・・・")
                    else:
                        break

                if timeout:
                    break

                if reply.author != teban_member:
                    continue

                operate = list(reply.content)
                try:
                    x = int(operate[0])
                    y = int(operate[1])

                except (IndexError, ValueError):
                    await message.channel.send("画像内の数字を入力してください")
                    continue

                if x <= 0 or x > size or y <= 0 or y > size:
                    await message.channel.send("画像内にある数字を入力してください")
                    continue

                place = match[x][y]
                if not place == 3:
                    await message.channel.send("そこは置けません")
                    continue

                break

            if timeout:
                break

            match[x][y] = index + 1 #石を置く

            #置けるところを表示していたが、ここで消す
            for line in match:
                temp = 0
                for cell in line:
                    if cell == 3:
                        line[temp] = 0
                    temp += 1

            #反転の判定
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    check = match[x+i][y+j]
                    reverse_list = []
                    if check == 2 - index:
                        reverse_list.append((x+i, y+j))
                        temp = 2
                        while True:
                            if match[x+i*temp][y+j*temp] == 0: #向かった先に何もなかったら
                                break
                            elif match[x+i*temp][y+j*temp] == 2 - index: #向かった先も相手の色がだったら
                                reverse_list.append((x+i*temp, y+j*temp))
                                temp += 1
                            else: #向かった先に自分の色があったら
                                for r in reverse_list:
                                    match[r[0]][r[1]] = index + 1 #自分の色にする
                                break

        else: #パスの時の動作
            if series_pass:
                b = 0
                w = 0
                for line in match[1:size+1]:
                    for cell in line[1:size+1]:
                        if cell == 1:
                            b += 1
                        elif cell == 2:
                            w += 1
                msg = (
                    "連続パス！試合終了！\n"
                    f"{sente.name}: {b}\n"
                    f"{gote.name}: {w}"
                )
                await message.channel.send(f"{msg}")
                break
            series_pass = True
            await message.channel.send(f"{teban_member.name}さんはパス！")

        #次に置けるところの探索
        x = 1
        for line in match[1:size+1]:
            y = 1
            for cell in line[1:size+1]:
                if cell == 2- index: #今の手番の相手の石を見つけたら
                    for i in (-1, 0, 1):
                        for j in (-1, 0, 1):
                            check = match[x+i][y+j] #見つかった石の周り8方向をcheck(自身もチェック対象になるが次のifではじかれる)
                            if check == index + 1: #自身の周りに相手の石を見つけたら
                                #(x, y) -> 自身
                                #(x+i, y+j) -> 自身の周りの石
                                temp = 2
                                #whileが始まる時、既に進むべき道は決まっているので1方向だけを見ればいい(*temp)
                                while True:
                                    if match[x+i*temp][y+j*temp] == 2 - index: #向かった先が自分の色なら
                                        break
                                    elif match[x+i*temp][y+j*temp] == index + 1: #向かった先も相手の色がだったら
                                        temp += 1
                                    else: #向かった先に何もなかったら
                                        match[x+i*temp][y+j*temp] = 3
                                        break
                y += 1
            x += 1

        finish = True
        for line in match[1:size+1]:
            for cell in line[1:size+1]:
                if cell == 0 or cell == 3:
                    finish = False
                    break
            if not finish:
                break

        if finish:
            create_pic_othello(match, size)
            f = discord.File("./game_pic/othello.png")
            b = 0
            w = 0
            for line in match[1:size+1]:
                for cell in line[1:size+1]:
                    if cell == 1:
                        b += 1
                    elif cell == 2:
                        w += 1
            msg = (
                f"{sente.name}: {b}\n"
                f"{gote.name}: {w}"
            )
            await message.channel.send(msg, file=f)
            break

        n += 1

    about_othello.clear()