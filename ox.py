import asyncio
import copy
import random

import discord
from PIL import Image, ImageDraw, ImageFont

def create_pic_ox(match, size):
    of = Image.open("./ox/o.png")
    xf = Image.open("./ox/x.png")
    nullf = Image.open("./ox/null.png")
    background = Image.new("RGB", (size*50, size*50))

    moji = ImageDraw.Draw(background)
    x = 0
    for line in match:
        y = 0
        for cell in line:
            if cell == 1:
                background.paste(of, (x*50, y*50))
            elif cell == -1:
                background.paste(xf, (x*50, y*50))
            else:
                background.paste(nullf, (x*50, y*50))
                font = ImageFont.truetype("./UDDigiKyokashoN-R.ttc", size=32)
                moji.text((x*50+9, y*50+9), text=f"{x+1}{y+1}", font=font, fill=0x000000)
            y += 1
        x += 1

    background.save("./game_pic/ox.png")


async def match_ox(client3, message, about_ox):
    size = about_ox[1]
    match = [[0] * size for i in range(size)]

    temp = random.choice((2, 3))
    sente = about_ox[temp]
    gote = about_ox[5-temp]
    await message.channel.send(f"先手は{sente.name}さん\n後手は{gote.name}さんです")

    player_list = []
    player_list.append(sente)
    player_list.append(gote)


    def check(m):
        return m.channel == message.channel and not m.author.bot

    finish = False
    for n in range(size**2):
        index = n % 2
        teban_member = player_list[index]
        create_pic_ox(match, size)
        f = discord.File("./game_pic/ox.png")
        await message.channel.send(f"{teban_member.name}さんの番です", file=f)
        while True:
            timeout = False
            for remain_time in (50, 10):
                try:
                    reply = await client3.wait_for("message", check=check, timeout=remain_time)
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
                x = int(operate[0]) - 1
                y = int(operate[1]) - 1

            except (IndexError, ValueError):
                await message.channel.send("画像内の数字を入力してください")
                continue

            item = index * -2 + 1
            try:
                cell = match[x][y]
            except IndexError:
                await message.channel.send("画像内の数字を入力してください")
                continue

            if cell != 0:
                await message.channel.send("そこは埋まっています")
                continue

            break

        if timeout:
            break

        match[x][y] = item

        finish = False
        #横の判定
        for line in match:
            if sum(line) == 3 * ( 1- (2 * index)):
                create_pic_ox(match, size)
                f = discord.File("./game_pic/ox.png")
                await message.channel.send(f"{player_list[index].name}の勝ち！", file=f)
                finish = True
                break

        if not finish:
            #縦の判定
            for i in range(size):
                s = 0
                for line in match:
                    s += line[i]
                if s == 3 * ( 1- (2 * index)):
                    create_pic_ox(match, size)
                    f = discord.File("./game_pic/ox.png")
                    await message.channel.send(f"{player_list[index].name}の勝ち！", file=f)
                    finish = True
                    break


        if not finish:
            #斜めの判定
            s1 = 0
            s2 = 0
            for i in range(size):
                s1 += match[i][i]
                if s1 == 3 * ( 1- (2 * index)):
                    create_pic_ox(match, size)
                    f = discord.File("./game_pic/ox.png")
                    await message.channel.send(f"{player_list[index].name}の勝ち！", file=f)
                    finish = True
                    break

                s2 += match[i][size-1-i]
                if s2 == 3 * ( 1- (2 * index)):
                    create_pic_ox(match, size)
                    f = discord.File("./game_pic/ox.png")
                    await message.channel.send(f"{player_list[index].name}の勝ち！", file=f)
                    finish = True
                    break

        if finish:
            break

    if not timeout and not finish:
        await message.channel.send("引き分け！", file=f)

    about_ox.clear()