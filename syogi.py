import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_syogi(match, index):
    ban = Image.open("./syogi/ban.png")

    j = 0
    for line in match[0:9]:
        i = 0
        for cell in line:
            if cell == 0:
                pass
            else:
                koma = abs(cell)
                koma = Image.open(f"./syogi/{koma}.png")
                if cell > 0: #先手なら
                    ban.paste(koma, (i+125, j+2), koma.split()[3])
                else: #後手なら
                    koma = koma.rotate(180)
                    ban.paste(koma, (i+125, j+18), koma.split()[3])
            i += 60
        j += 80

    moji = ImageDraw.Draw(ban)
    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
    #先手の持ち駒を描画
    for i in range(7):
        koma = Image.open(f"./syogi/{7-i}.png")
        ban.paste(koma, (670, i*80+130), koma.split()[3])
        moji.text((720, i*80+150), text=f"×{match[9][6-i]}", font=font, fill=0x000000)

    #後手の持ち駒を描画
    for i in range(7):
        temp = Image.new("RGB", (60, 32), color=0x16b7ff)
        moji = ImageDraw.Draw(temp)
        koma = Image.open(f"./syogi/{i+1}.png")
        koma = koma.rotate(180)
        ban.paste(koma, (60, i*80+40), koma.split()[3])
        moji.text((0, 0), text=f"×{match[10][i]}", font=font, fill=0x000000)
        ban.paste(temp.rotate(180), (0, i*80+58))

    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=20)
    if index == 0: #手番が先手なら
        moji = ImageDraw.Draw(ban)
        y = 1
        for line in match[0:9]:
            x = 1
            for cell in line:
                if cell == 0:
                    moji.text(((x-1)*60+140, (y-1)*80+30), text=f"{x}{y}", font=font, fill=0x000000)
                elif cell > 0:
                    moji.text(((x-1)*60+140, (y-1)*80+58), text=f"{x}{y}", font=font, fill=0x000000)
                elif cell < 0:
                    moji.text(((x-1)*60+140, (y-1)*80+2), text=f"{x}{y}", font=font, fill=0x000000)
                x += 1
            y += 1

        font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
        moji.text((680, 20), text="先手", font=font, fill=0x000000)
        moji.text((36, 668), text="後手", font=font, fill=0x000000)

    else: #後手なら
        ban = ban.rotate(180)
        moji = ImageDraw.Draw(ban)
        y = 1
        for line in match[0:9]:
            x = 1
            for cell in line:
                if cell == 0:
                    moji.text((680-(x*60), 750-(y*80)), text=f"{x}{y}", font=font, fill=0x000000)
                elif cell > 0:
                    moji.text((680-(x*60), 722-(y*80)), text=f"{x}{y}", font=font, fill=0x000000)
                elif cell < 0:
                    moji.text((680-(x*60), 778-(y*80)), text=f"{x}{y}", font=font, fill=0x000000)
                x += 1
            y += 1

        font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
        moji.text((680, 20), text="後手", font=font, fill=0x000000)
        moji.text((36, 668), text="先手", font=font, fill=0x000000)

    ban.save("./game_pic/syogi.png")


async def match_syogi(client3, message, about_syogi):
    match = [
        [-2, -3, -4, -5, -16, -5, -4, -3, -2],
        [0, -7, 0, 0, 0, 0, 0, -6, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 6, 0, 0, 0, 0, 0, 7, 0],
        [2, 3, 4, 5, 15, 5, 4, 3, 2],
        [0, 0, 0, 0, 0, 0, 0], #先手の持ち駒
        [0, 0, 0, 0, 0, 0, 0] #後手の持ち駒
    ]

    temp = random.choice((1, 2))
    sente = about_syogi[temp]
    gote = about_syogi[3-temp]
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
        create_pic_syogi(match, index)
        f = discord.File("./game_pic/syogi.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)

        while True:
            timeout = False
            for remain_time in (60, 50, 10):
                try:
                    reply = await client3.wait_for("message", check=msg_check, timeout=remain_time)
                except asyncio.TimeoutError:
                    if remain_time == 10:
                        next_index = (n+1)%2
                        await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                        timeout = True
                        break
                    elif remain_time == 50:
                        await message.channel.send("残り10秒")
                    else:
                        await message.channel.send("60秒経過")
                else:
                    break

            if timeout:
                break

            if reply.author != teban_member:
                continue

            if reply.content == "投了":
                msg = await message.channel.send("投了しますか？")
                await msg.add_reaction("👍")
                await msg.add_reaction("👎")
                def check2(reaction, user):
                    return user.id == teban_member.id and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
                try:
                    reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
                except asyncio.TimeoutError:
                    next_index = (n+1)%2
                    await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                    timeout = True
                    break
                else:
                    if str(reaction.emoji) == "👍": #投了するなら
                        next_index = (n+1)%2
                        await message.channel.send(f"タイムアウト！{player_list[next_index]}の勝ち！")
                        timeout = True #タイムアウトではない
                        break

                    else:
                        await message.channel.send("次の一手を指してください")
                        continue

            #x_beforeを判定
            #intキャストできれば良い
            try:
                x_before = int(reply.content[0:1]) - 1
            except ValueError:
                await message.channel.send("画像内にある数字か0駒xy(最初の0は駒打ちを意味する)(駒は[歩,香,桂,銀,金,角,飛])(1≦x, y≦9)、又は「投了」を入力してください")
                continue

            #x_after, y_afterを判定
            #intキャストできれば良い
            try:
                x_after = int(reply.content[2:3]) - 1
                y_after = int(reply.content[3:4]) - 1
            except ValueError:
                await message.channel.send("画像内にある数字か0駒xy(最初の0は駒打ちを意味する)(駒は[歩,香,桂,銀,金,角,飛])(1≦x, y≦9)、又は「投了」を入力してください")
                continue

            try:
                y_before = int(reply.content[1:2]) - 1
            except ValueError:
                y_before = reply.content[1:2]
                if not x_before == -1 and any(
                    (
                        y_before == "歩", y_before == "香",
                        y_before == "桂", y_before == "銀",
                        y_before == "金", y_before == "角", y_before == "飛"
                    )
                ):
                    await message.channel.send("画像内にある数字か0駒xy(最初の0は駒打ちを意味する)(駒は[歩,香,桂,銀,金,角,飛])(1≦x, y≦9)、又は「投了」を入力してください")
                    continue

            if not x_before == -1: #駒打ちでない(=盤上の駒を動かす)なら
                if any(
                    (
                        x_before <= -1, x_before >= 9,
                        y_before <= -1, y_before >= 9,
                        x_after <= -1, x_after >= 9,
                        y_after <= -1, y_after >= 9
                    )
                ):
                    await message.channel.send("画像内にある数字か0駒xy(最初の0は駒打ちを意味する)(駒は[歩,香,桂,銀,金,角,飛])(1≦x, y≦9)、又は「投了」を入力してください")
                    continue

            if x_before == -1: #駒打ちなら
                if y_before == "歩":
                    place = 0
                elif y_before == "香":
                    place = 1
                elif y_before == "桂":
                    place = 2
                elif y_before == "銀":
                    place = 3
                elif y_before == "金":
                    place = 4
                elif y_before == "角":
                    place = 5
                elif y_before == "飛":
                    place = 6
                if match[index+9][place] == 0:
                    await message.channel.send("その駒は持ち駒にありません")
                    continue

                if not match[y_after][x_after] == 0:
                    await message.channel.send("そこは打てません")
                    continue

                if place == 0 or place == 1: #歩と香なら
                    if y_after == index * 8: #相手の最下段なら
                        await message.channel.send("行きどころのない駒は打てません")
                        continue

                elif place == 2: #桂なら
                    if index == 0 and y_after <= 1 or index == 1 and y_after >= 7:
                        await message.channel.send("行きどころのない駒は打てません")
                        continue

            else: #盤上の駒を動かすなら
                before = match[y_before][x_before]
                after = match[y_after][x_after]
                if before == 0:
                    await message.channel.send("そこに駒はありません")
                    continue

                elif index == 0 and before < 0: #先手が相手の駒を動かそうとしたら
                    await message.channel.send("その駒は動かせません")
                    continue

                elif index == 1 and before > 0: #後手が相手の駒を動かそうとしたら
                    await message.channel.send("その駒は動かせません")
                    continue

                elif index == 0 and after > 0: #先手が自分の駒を取ろうとしたら
                    await message.channel.send("その駒は取れません")
                    continue

                elif index == 1 and after < 0: #後手が自分の駒を取ろうとしたら
                    await message.channel.send("その駒は取れません")
                    continue

                #駒が動かせる時
                if index == 0: #先手の時
                    can_go = True
                    if before == 1: #歩
                        if not (x_before == x_after and y_before == y_after+1):
                            can_go = False

                    elif before == 2: #香
                        if not (x_before == x_after and y_before > y_after):
                            can_go = False
                        else:
                            for i in range(y_before-y_after-1):
                                check = match[y_before-i-1][x_before]
                                if not check == 0:
                                    can_go = False
                                    break

                    elif before == 3: #桂
                        if not ((x_before == x_after+1) or (x_before == x_after-1) and y_before == y_after+2):
                            can_go = False

                    elif before == 4: #銀
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after+1), #前
                                (x_before == x_after-1 and y_before == y_after+1), #右前
                                (x_before == x_after+1 and y_before == y_after+1), #左前
                                (x_before == x_after-1 and y_before == y_after-1), #右後
                                (x_before == x_after+1 and y_before == y_after-1) #左後
                            )
                        ):
                            can_go = False

                    elif any((before == 5, before == 8, before == 9, before == 10, before == 11)): #金、と金、成香、成桂、成銀
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after+1), #前
                                (x_before == x_after-1 and y_before == y_after+1), #右前
                                (x_before == x_after+1 and y_before == y_after+1), #左前
                                (x_before == x_after-1 and y_before == y_after), #右
                                (x_before == x_after+1 and y_before == y_after), #左
                                (x_before == x_after and y_before == y_after-1) #後
                            )
                        ):
                            can_go = False

                    elif before == 6: #角:
                        if not (abs(x_after-x_before) == abs(y_after-y_before)):
                            can_go = False

                        else:
                            if x_after - x_before > 0: #右に行ってたら
                                x = 1
                            else: #左に行ってたら
                                x = -1
                            if y_after - y_before > 0: #後ろに行ってたら
                                y = 1
                            else: #前に行ってたら
                                y = -1
                            for i in range(abs(x_after-x_before)-1):
                                check = match[y_before+((i+1)*y)][x_before+((i+1)*x)]
                                if not check == 0:
                                    can_go = False
                                    break

                    elif before == 7: #飛車
                        if not (x_before == x_after or y_before == y_after):
                            can_go = False

                        else:
                            if x_before == x_after: #前後移動なら
                                if y_after - y_before > 0: #後ろに行ってたら
                                    y = 1
                                else: #前に行ってたら
                                    y = -1
                                for i in range(abs(y_after-y_before)-1):
                                    check = match[y_before+((i+1)*y)][x_before]
                                    if not check == 0:
                                        can_go = False
                                        break

                            elif y_before == y_after: #左右移動なら
                                if x_after - x_before > 0: #右に行ってたら
                                    x = 1
                                else: #左に行ってたら
                                    x = -1
                                for i in range(abs(x_after-x_before)-1):
                                    check = match[y_before][x_before+(i+1)*x]
                                    if not check == 0:
                                        can_go = False
                                        break

                    elif before == 13: #馬
                        if not any(
                            (
                                abs(x_after-x_before) == abs(y_after-y_before),
                                (x_before == x_after and y_before == y_after+1), #前
                                (x_before == x_after and y_before == y_after-1), #後
                                (x_before == x_after-1 and y_before == y_after), #右
                                (x_before == x_after+1 and y_before == y_after) #左
                            )
                        ):
                            can_go = False

                        else:
                            if abs(x_after-x_before) == abs(y_after-y_before):
                                if x_after - x_before > 0: #右に行ってたら
                                    x = 1
                                else: #左に行ってたら
                                    x = -1
                                if y_after - y_before > 0: #後ろに行ってたら
                                    y = 1
                                else: #前に行ってたら
                                    y = -1
                                for i in range(abs(x_after-x_before)-1):
                                    check = match[y_before+((i+1)*y)][x_before+((i+1)*x)]
                                    if not check == 0:
                                        can_go = False
                                        break

                    elif before == 14: #龍
                        if not any(
                            (
                                (x_before == x_after or y_before == y_after), #
                                (x_before == x_after-1 and y_before == y_after+1), #右前
                                (x_before == x_after+1 and y_before == y_after+1), #左前
                                (x_before == x_after-1 and y_before == y_after-1), #右後
                                (x_before == x_after+1 and y_before == y_after-1) #左後
                            )
                        ):
                            can_go = False

                        else:
                            if (x_before == x_after or y_before == y_after):
                                if x_before == x_after: #前後移動なら
                                    if y_after - y_before > 0: #後ろに行ってたら
                                        y = 1
                                    else: #前に行ってたら
                                        y = -1
                                    for i in range(abs(y_after-y_before)-1):
                                        check = match[y_before+((i+1)*y)][x_before]
                                        if not check == 0:
                                            can_go = False
                                            break
                                elif y_before == y_after: #左右移動なら
                                    if x_after - x_before > 0: #右に行ってたら
                                        x = 1
                                    else: #左に行ってたら
                                        x = -1
                                    for i in range(abs(x_after-x_before)-1):
                                        check = match[y_before][x_before+(i+1)*x]
                                        if not check == 0:
                                            can_go = False
                                            break

                    elif before == 15: #王
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after+1), #前
                                (x_before == x_after and y_before == y_after-1), #後ろ
                                (x_before == x_after-1 and y_before == y_after), #右
                                (x_before == x_after+1 and y_before == y_after), #左
                                (x_before == x_after-1 and y_before == y_after+1), #右前
                                (x_before == x_after+1 and y_before == y_after+1), #左前
                                (x_before == x_after-1 and y_before == y_after-1), #右後
                                (x_before == x_after+1 and y_before == y_after-1) #左後
                            )
                        ):
                            can_go = False

                elif index == 1: #後手の時
                    can_go = True
                    if before == -1: #歩
                        if not (x_before == x_after and y_before == y_after-1):
                            can_go = False

                    elif before == -2: #香
                        if not (x_before == x_after and y_before < y_after):
                            can_go = False
                        else:
                            for i in range(y_after-y_before-1):
                                check = match[y_before+i+1][x_before]
                                if not check == 0:
                                    can_go = False
                                    break

                    elif before == -3: #桂
                        if not ((x_before == x_after+1) or (x_before == x_after-1) and y_before == y_after-2):
                            can_go = False

                    elif before == -4: #銀
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after-1), #前
                                (x_before == x_after+1 and y_before == y_after-1), #右前
                                (x_before == x_after-1 and y_before == y_after-1), #左前
                                (x_before == x_after+1 and y_before == y_after+1), #右後
                                (x_before == x_after-1 and y_before == y_after+1) #左後
                            )
                        ):
                            can_go = False

                    elif any((before == -5, before == -8, before == -9, before == -10, before == -11)): #金、と金、成香、成桂、成銀
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after-1), #前
                                (x_before == x_after+1 and y_before == y_after-1), #右前
                                (x_before == x_after-1 and y_before == y_after-1), #左前
                                (x_before == x_after+1 and y_before == y_after), #右
                                (x_before == x_after-1 and y_before == y_after), #左
                                (x_before == x_after and y_before == y_after+1) #後
                            )
                        ):
                            can_go = False

                    elif before == -6: #角:
                        if not (abs(x_after-x_before) == abs(y_after-y_before)):
                            can_go = False
                        else:
                            if x_after - x_before < 0: #右に行ってたら
                                x = -1
                            else: #左に行ってたら
                                x = 1
                            if y_after - y_before < 0: #後に行ってたら
                                y = -1
                            else: #前に行ってたら
                                y = 1
                            for i in range(abs(x_after-x_before)-1):
                                check = match[y_before+((i+1)*y)][x_before+((i+1)*x)]
                                if not check == 0:
                                    can_go = False
                                    break

                    elif before == -7: #飛車
                        if not (x_before == x_after or y_before == y_after):
                            can_go = False

                        else:
                            if x_before == x_after: #前後移動なら
                                if y_after - y_before < 0: #後ろに行ってたら
                                    y = -1
                                else: #前に行ってたら
                                    y = 1
                                for i in range(abs(y_after-y_before)-1):
                                    check = match[y_before+((i+1)*y)][x_before]
                                    if not check == 0:
                                        can_go = False
                                        break

                            elif y_before == y_after: #左右移動なら
                                if x_after - x_before < 0: #右に行ってたら
                                    x = -1
                                else: #左に行ってたら
                                    x = 1
                                for i in range(abs(x_after-x_before)-1):
                                    check = match[y_before][x_before+(i+1)*x]
                                    if not check == 0:
                                        can_go = False
                                        break

                    elif before == -13: #馬
                        if not any(
                            (
                                abs(x_after-x_before) == abs(y_after-y_before),
                                (x_before == x_after and y_before == y_after-1), #前
                                (x_before == x_after and y_before == y_after+1), #後
                                (x_before == x_after+1 and y_before == y_after), #右
                                (x_before == x_after-1 and y_before == y_after), #左
                            )
                        ):
                            can_go = False

                        else:
                            if abs(x_after-x_before) == abs(y_after-y_before):
                                if x_after - x_before < 0: #右に行ってたら
                                    x = -1
                                else: #左に行ってたら
                                    x = 1
                                if y_after - y_before < 0: #後に行ってたら
                                    y = -1
                                else: #前に行ってたら
                                    y = 1
                                for i in range(abs(x_after-x_before)-1):
                                    check = match[y_before+((i+1)*y)][x_before+((i+1)*x)]
                                    if not check == 0:
                                        can_go = False
                                        break

                    elif before == -14: #龍
                        if not any(
                            (
                                (x_before == x_after or y_before == y_after),
                                (x_before == x_after+1 and y_before == y_after-1), #右前
                                (x_before == x_after-1 and y_before == y_after-1), #左前
                                (x_before == x_after+1 and y_before == y_after+1), #右後
                                (x_before == x_after-1 and y_before == y_after+1) #左後
                            )
                        ):
                            can_go = False

                        else:
                            if (x_before == x_after or y_before == y_after):
                                if x_before == x_after: #前後移動なら
                                    if y_after - y_before < 0: #後ろに行ってたら
                                        y = -1
                                    else: #前に行ってたら
                                        y = 1
                                    for i in range(abs(y_after-y_before)-1):
                                        check = match[y_before+((i+1)*y)][x_before]
                                        if not check == 0:
                                            can_go = False
                                            break
                                elif y_before == y_after: #左右移動なら
                                    if x_after - x_before < 0: #右に行ってたら
                                        x = -1
                                    else: #左に行ってたら
                                        x = 1
                                    for i in range(abs(x_after-x_before)-1):
                                        check = match[y_before][x_before+(i+1)*x]
                                        if not check == 0:
                                            can_go = False
                                            break

                    elif before == -16: #玉
                            #前
                        if not any(
                            (
                                (x_before == x_after and y_before == y_after-1), #前
                                (x_before == x_after and y_before == y_after+1), #後
                                (x_before == x_after+1 and y_before == y_after), #右
                                (x_before == x_after-1 and y_before == y_after), #左
                                (x_before == x_after+1 and y_before == y_after-1), #右前
                                (x_before == x_after-1 and y_before == y_after-1), #左前
                                (x_before == x_after+1 and y_before == y_after+1), #右後
                                (x_before == x_after-1 and y_before == y_after+1) #左後
                            )
                        ):
                            can_go = False

                if not can_go:
                    await message.channel.send("そこには行けません")
                    continue

            break

        if timeout:
            break

        if x_before == -1: #駒打ちなら
            match[index+9][place] =- 1 #持ち駒を1減らす
            if index == 0: #先手なら
                match[y_after][x_after] = place + 1
            else: #後手なら
                match[y_after][x_after] = (place + 1) * -1

        else: #盤上の駒を動かしたら
            #駒を取った時
            if not after == 0:
                if after == -16:
                    await message.channel.send(f"{sente.name}の勝ち！")
                    break
                elif after == 15:
                    await message.channel.send(f"{gote.name}の勝ち！")
                    break
                elif abs(after) >= 8 and abs(after) <= 14:
                    after = abs(after) - 7
                else:
                    after = abs(after)
                match[index+9][after-1] += 1

                #ここまで終わり

            if abs(before) == 1 or abs(before) == 2 or abs(before) == 3 or abs(before) == 4 or abs(before) == 6 or abs(before) ==7: #動かすのが成ることができる駒なら
                def check2(reaction, user):
                    return user.id == teban_member.id and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
                if (index == 0 and (y_before <= 2 or y_after <= 2)) or (index == 1 and (y_before >= 6 or y_after >= 6)): #成る条件を満たしていたら
                    msg = await message.channel.send("成りますか？")
                    await msg.add_reaction("👍")
                    await msg.add_reaction("👎")
                    try:
                        reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
                    except asyncio.TimeoutError:
                        index = (n+1)%2
                        await message.channel.send(f"タイムアウト！{player_list[index]}の勝ち！")
                        timeout = True
                        break
                    else:
                        if str(reaction.emoji) == "👍": #成るなら
                            if index == 0:
                                before += 7
                            else:
                                before -= 7


            match[y_after][x_after] = before
            match[y_before][x_before] = 0

        n += 1

    about_syogi.clear()