import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_contrast(match, index, sente_name, gote_name):
    ban = Image.open("./contrast/ban.png")
    y = 0
    for line in match[0:5]:
        x = 0
        for cell in line:
            if cell[1] == "white":
                koma = Image.open("./contrast/koma_white.png")
            elif cell[1] == "gray":
                koma = Image.open("./contrast/koma_gray.png")
                bg = Image.open("./contrast/cell_gray.png")
                ban.paste(bg, (x*50+104, y*70+54))
            else:
                koma = Image.open("./contrast/koma_black.png")
                bg = Image.open("./contrast/cell_black.png")
                ban.paste(bg, (x*50+104, y*70+54))

            if cell[0] == -1:
                koma = koma.rotate(180)
                ban.paste(koma, (x*50+100, y*70+70), koma.split()[3])

            elif cell[0] == 1:
                ban.paste(koma, (x*50+100, y*70+50), koma.split()[3])

            x += 1
        y += 1

    #持ち板を表示
    #先手の持ち板を表示
    bg_y = 335
    for i in range(match[5][0]):
        bg = Image.open("./contrast/cell_black.png")
        ban.paste(bg, (355, bg_y))
        bg_y -= 70
    if match[5][1] == 1:
        bg = Image.open("./contrast/cell_gray.png")
        ban.paste(bg, (355, bg_y))

    #後手の持ち板を表示
    bg_y = 55
    for i in range(match[6][0]):
        bg = Image.open("./contrast/cell_black.png")
        ban.paste(bg, (55, bg_y))
        bg_y += 70
    if match[6][1] == 1:
        bg = Image.open("./contrast/cell_gray.png")
        ban.paste(bg, (55, bg_y))

    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
    if index == 1:
        ban = ban.rotate(180)
        moji = ImageDraw.Draw(ban)
        moji.text((441-len(gote_name)*32, 409), text=gote_name, font=font, fill=0x000000)
        moji.text((9, 9), text=sente_name, font=font, fill=0x000000)
    else:
        moji = ImageDraw.Draw(ban)
        moji.text((441-len(sente_name)*32, 409), text=sente_name, font=font, fill=0x000000)
        moji.text((9, 9), text=gote_name, font=font, fill=0x000000)

    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=20)
    y = 0
    for line in match[0:5]:
        x = 0
        for cell in line:
            if cell[1] == "white":
                str_color = 0x000000
            elif cell[1] == "gray":
                str_color = 0x000000
            else:
                str_color = 0xffffff

            if cell[0] == 2:
                str_color = 0x0000ff

            if index == 0:
                if cell[0] == -1:
                    moji.text((x*50+115, y*70+52), text=f"{x+1}{y+1}", font=font, fill=str_color)
                elif cell[0] == 0:
                    moji.text((x*50+115, y*70+75), text=f"{x+1}{y+1}", font=font,  fill=str_color)
                else:
                    moji.text((x*50+115, y*70+98), text=f"{x+1}{y+1}", font=font,  fill=str_color)
            else:
                if cell[0] == -1:
                    moji.text(((4-x)*50+115, (4-y)*70+98), text=f"{x+1}{y+1}", font=font,  fill=str_color)
                elif cell[0] == 0:
                    moji.text(((4-x)*50+115, (4-y)*70+75), text=f"{x+1}{y+1}", font=font,  fill=str_color)
                else:
                    moji.text(((4-x)*50+115, (4-y)*70+52), text=f"{x+1}{y+1}", font=font,  fill=str_color)

            x += 1
        y += 1
    
    ban.save("./game_pic/contrast.png")


async def match_contrast(client3, message, about_contrast):
    match = [
        [[-1, "white"], [-1, "white"], [-1, "white"], [-1, "white"], [-1, "white"]],
        [[0, "white"], [0, "white"], [0, "white"], [0, "white"], [0, "white"]],
        [[0, "white"], [0, "white"], [0, "white"], [0, "white"], [0, "white"]],
        [[0, "white"], [0, "white"], [0, "white"], [0, "white"], [0, "white"]],
        [[1, "white"], [1, "white"], [1, "white"], [1, "white"], [1, "white"]],
        [3, 1], #先手の持ち板
        [3, 1] #後手の持ち板
    ]

    temp = random.choice((1, 2))
    sente = about_contrast[temp]
    gote = about_contrast[3-temp]
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
        create_pic_contrast(match, index, sente.display_name, gote.display_name)
        f = discord.File("./game_pic/contrast.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)

        while True:
            timeout = False
            for remain_time in (120, 50, 10):
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
                        await message.channel.send("120秒経過")
                else:
                    break

            if timeout: #不要に見えている、おまじない
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

            try:
                x_before = int(reply.content[0:1]) - 1
                y_before = int(reply.content[1:2]) - 1
                x_after = int(reply.content[2:3]) - 1
                y_after = int(reply.content[3:4]) - 1
            except ValueError:
                await message.channel.send("画像内にある数字を入力してください")
                continue
            except IndexError:
                await message.channel.send("移動の指定方法は動かしたい駒の数字+移動先の数字です。(例: 3534)")
                continue

            if min(x_before, y_before, x_after, y_after) < 0 or max(x_before, y_before, x_after, y_after) > 4:
                await message.channel.send("画像内にある数字を入力してください")
                continue

            before = match[y_before][x_before]
            after = match[y_after][x_after]

            if before[0] == 0:
                await message.channel.send("そこに駒はありません")
                continue

            current_player_koma = 1 - (2 * index)
            if before[0] != current_player_koma:
                await message.channel.send("その駒は動かせません")
                continue

            if after[0] != 0:
                await message.channel.send("そこには動かせません")
                continue

            tile_type = match[y_before][x_before][1]
            x_diff = x_after - x_before
            y_diff = y_after - y_before
            if tile_type == "white":
                if not (x_diff == 0 or y_diff == 0):
                    await message.channel.send("そこには動かせません")
                    continue
 
                can_next = True
                for i in range(1, abs(x_diff)+1):
                    if x_diff < 0:
                        i = i * -1
                    if y_before == y_after and x_before+i == x_after:
                        pass
                    elif match[y_before][x_before+i][0] != current_player_koma:
                        await message.channel.send("そこには動かせません")
                        can_next = False
                        break
                if not can_next:
                    continue

                for i in range(1, abs(y_diff)+1 ):
                    if y_diff < 0:
                        i = i * -1
                    if y_before+i == y_after and x_before == x_after:
                        pass
                    elif match[y_before+i][x_before][0] != current_player_koma:
                        await message.channel.send("そこには動かせません")
                        can_next = False
                        break
                if not can_next:
                    continue

            elif tile_type == "black":
                if abs(x_diff) != abs(y_diff):
                    await message.channel.send("そこには動かせません")
                    continue

                can_next = True
                for i in range(1, abs(x_diff)+1):
                    j = i
                    if x_diff < 0:
                        i = i * -1
                    if y_diff < 0:
                        j = j * -1

                    if y_before+j == y_after and x_before+i == x_after:
                        pass
                    elif match[y_before+j][x_before+i][0] != current_player_koma:
                        await message.channel.send("そこには動かせません")
                        can_next = False
                        break
                    
                if not can_next:
                    continue

            else:
                if x_diff == 0 or y_diff == 0: 
                    can_next = True
                    for i in range(1, abs(x_diff)+1):
                        if x_diff < 0:
                            i = i * -1
                        if y_before == y_after and x_before+i == x_after:
                            pass
                        elif match[y_before][x_before+i][0] != current_player_koma:
                            await message.channel.send("そこには動かせません")
                            can_next = False
                            break
                    if not can_next:
                        continue

                    for i in range(1, abs(y_diff)+1 ):
                        if y_diff < 0:
                            i = i * -1
                        if y_before+i == y_after and x_before == x_after:
                            pass
                        elif match[y_before+i][x_before][0] != current_player_koma:
                            await message.channel.send("そこには動かせません")
                            can_next = False
                            break
                    if not can_next:
                        continue
                
                elif abs(x_diff) == abs(y_diff):
                    can_next = True
                    for i in range(1, abs(x_diff)+1):
                        j = i
                        if x_diff < 0:
                            i = i * -1
                        if y_diff < 0:
                            j = j * -1

                        if y_before+j == y_after and x_before+i == x_after:
                            pass
                        elif match[y_before+j][x_before+i][0] != current_player_koma:
                            await message.channel.send("そこには動かせません")
                            can_next = False
                            break
                        
                    if not can_next:
                        continue
                
                else:
                    await message.channel.send("そこには動かせません")
                    continue

            break

        if timeout:
            break

        match[y_before][x_before][0] = 0
        match[y_after][x_after][0] = current_player_koma

        #勝敗判定をはさむ
        if index == 0:
            if y_after == 0:
                create_pic_contrast(match, index, sente.display_name, gote.display_name)
                f = discord.File("./game_pic/contrast.png")
                await message.channel.send(f"{sente.name}の勝ち！", file=f)
                break
        else:
            if y_after == 4:
                create_pic_contrast(match, index, sente.display_name, gote.display_name)
                f = discord.File("./game_pic/contrast.png")
                await message.channel.send(f"{gote.name}の勝ち！", file=f)
                break

        #板を置くかの選択を迫る
        if match[index+5] != [0, 0]:
            def check3(reaction, user):
                return user.id == teban_member.id and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")

            msg = await message.channel.send("タイルを設置しますか？(30秒アクションなしでタイムアウト)")
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
            try:
                reaction, user = await client3.wait_for("reaction_add", check=check3, timeout=30)
            except asyncio.TimeoutError:
                index = (n+1)%2
                await message.channel.send(f"タイムアウト！{player_list[index]}の勝ち！")
                timeout = True
                break

            await msg.delete()
            if str(reaction.emoji) == "👍": #タイルを設置するなら
                await message.channel.send("設置場所の数字と設置するタイルの色(G. B)を入力してください(例: 33B(33に黒のタイルを設置))")
                while True:
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

                        break

                    try:
                        place_x = int(reply.content[0:1]) - 1
                        place_y = int(reply.content[1:2]) - 1
                    except ValueError:
                        await message.channel.send("画像内にある数字を入力してください")
                        continue
                    except IndexError:
                        await message.channel.send("設置場所の数字と設置するタイルの色(G. B)を入力してください(例: 33B(33に黒のタイルを設置))")
                        continue

                    if place_x < 0 or place_x > 4 or place_y < 0 or place_y > 4:
                        await message.channel.send("画像内にある数字を入力してください")
                        continue

                    if match[place_y][place_x][0] != 0 or match[place_y][place_x][1] != "white":
                        await message.channel.send("そこにタイルを設置することはできません")
                        continue                            

                    try:
                        place_color = reply.content[2:3].upper()
                    except IndexError:
                        await message.channel.send("設置場所の数字と設置するタイルの色(G. B)を入力してください(例: 33B(33に黒のタイルを設置))")
                        continue

                    if place_color == "B":
                        if match[index+5][0] == 0:
                            await message.channel.send("あなたは黒色のタイルを持っていません")
                            continue

                    elif place_color == "G":
                        if match[index+5][1] == 0:
                            await message.channel.send("あなたは灰色のタイルを持っていません")
                            continue
                    else:
                        await message.channel.send("色はG(灰色)かB(黒色)です")
                        continue

                    break

                if place_color == "B":
                    match[place_y][place_x][1] = "black"
                    match[index+5][0] -= 1
                else:
                    match[place_y][place_x][1] = "gray"
                    match[index+5][1] -= 1

        n += 1
    
    about_contrast.clear()