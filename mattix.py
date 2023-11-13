import asyncio
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_mattix(match, size):
    background = Image.new("RGB", size=(50*size, 60*size), color=0x000000)
    cell = Image.open("./mattix/cell.png")
    chip = Image.open("./mattix/chip.png")
    cloth = Image.open("./mattix/cloth.png")
    moji = ImageDraw.Draw(background)
    font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=30)
    font2 = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=20)
    for i in range(size):
        for j in range(size):
            background.paste(cell, (j*50, i*60))
            if match[j][i] == 0:
                background.paste(cloth, (j*50, i*60), cloth.split()[3])
            elif match[j][i] is not None:
                background.paste(chip, (j*50, i*60), chip.split()[3])
                text = f"{match[j][i]}"
                if len(text) == 3:
                    moji.text((50*j, 60*i+10), text=text, font=font, fill=0xffffff)
                elif len(text) == 2:
                    moji.text((50*j+10, 60*i+10), text=text, font=font, fill=0xffffff)
                else:
                    moji.text((50*j+20, 60*i+10), text=text, font=font, fill=0xffffff)

            moji.text((50*j+15, 60*i+40), text=f"{j+1}{i+1}", font=font2, fill=0x00ffff, stroke_width=2, stroke_fill=0x000000)

    background.save("./game_pic/mattix.png")


async def match_mattix(client3, message, about_mattix):
    mode = about_mattix[1]
    if mode == "basic":
        size = 4
        num_tuple = (0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8)
        random_num_list = random.sample(num_tuple, k=16)
        match = []
        for i in range(4):
            match.append(random_num_list[i*4:(i+1)*4])

    else:
        size = 6
        num_tuple = (0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 1, 2, 3, 8, 9, 9, 10, -1, -1, -2, -2, -3, -3, -4, -5, -6, -7, -8, -9, -10)
        random_num_list = random.sample(num_tuple, k=36)
        match = []
        for i in range(6):
            match.append(random_num_list[i*6:(i+1)*6])

    temp = random.choice((2, 3))
    sente = about_mattix[temp]
    gote = about_mattix[5-temp]
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)

    def msg_check(m):
        return m.channel == message.channel and not m.author.bot
    
    sente_point = 0
    gote_point = 0
    n = 0
    while True:
        index = n % 2
        teban_member = player_list[index]
        create_pic_mattix(match, size)
        f = discord.File("./game_pic/mattix.png")
        await message.channel.send(f"{teban_member.name}さんの番です\n{sente.name}: {sente_point}\n{gote.name}: {gote_point}", file=f)
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
                x = int(operate[1]) - 1
                y = int(operate[0]) - 1

            except (IndexError, ValueError):
                await message.channel.send("画像内の数字を入力してください1")
                continue

            if x < 0 or x > size or y < 0 or y > size:
                await message.channel.send("画像内にある数字を入力してください2")
                continue

            for i in range(size):
                for j in range(size):
                    if match[j][i] == 0:
                        cloth_x = i
                        cloth_y = j
                        break

            if x == cloth_x and y == cloth_y:
                await message.channel.send("動いてください")
                continue

            if match[y][x] is None:
                await message.channel.send("そこへは動けません")
                continue

            if x != cloth_x and y != cloth_y:
                await message.channel.send("そこへは動けません")
                continue

            break

        if timeout:
            break

        if teban_member == sente:
            sente_point += match[y][x]
        else:
            gote_point += match[y][x]
        match[y][x] = 0
        match[cloth_y][cloth_x] = None

        finish = True
        for i in range(size):
            if match[y][i] != 0 and match[y][i] is not None or match[i][x] != 0 and match[i][x] is not None:
                finish = False
                break

        if finish:
            create_pic_mattix(match, size)
            f = discord.File("./game_pic/mattix.png")
            msg = (
                f"{sente.name}: {sente_point}\n"
                f"{gote.name}: {gote_point}"
            )
            await message.channel.send(msg, file=f)
            break

        n += 1

    about_mattix.clear()