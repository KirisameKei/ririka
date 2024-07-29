import datetime
import json
import os
import random
import traceback

import discord
import requests
from discord.ext import tasks

import contrast
import mattix
import othello
import ox
import syogi
import quoridor
import uno

os.chdir(os.path.dirname(os.path.abspath(__file__)))
client3 = discord.Client(intents=discord.Intents.all())

where_from = os.getenv("where_from")
error_notice_webhook_url = os.getenv("error_notice_webhook")

now_playing = False
about_ox = [] #[datetime.datetime, int, discord.Member, discord.Member]
about_othello = [] #[datetime.datetime, int, discord.Member, discord.Member]
about_syogi = [] #[datetime.datetime, discord.Member, discord.Member]
about_uno = [] #[datetime.datetime, discord.Message, bool, discord.Member × n]
about_quoridor = [] #[datetime.datetime, discord.Member, discord.Member]
about_contrast = [] #[datetime.datetime, discord.Member, discord.Member]
about_mattix = [] #[datetime.datetime, str, discord.Member, discord.Member]
about_puzzle15 = [] #[discord.Member]

def unexpected_error(msg=None):
    """
    予期せぬエラーが起きたときの対処
    エラーメッセージ全文と発生時刻を通知"""

    try:
        if msg is not None:
            content = (
                f"{msg.author}\n"
                f"{msg.content}\n"
                f"{msg.channel.name}\n"
            )
        else:
            content = ""
    except:
        unexpected_error()
        return

    now = datetime.datetime.now().strftime("%H:%M") #今何時？
    error_msg = f"```\n{traceback.format_exc()}```" #エラーメッセージ全文
    error_content = {
        "content": "<@523303776120209408>", #けいにメンション
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "embeds": [ #エラー内容・発生時間まとめ
            {
                "title": "エラーが発生しました",
                "description": content + error_msg,
                "color": 0xff0000,
                "footer": {
                    "text": now
                }
            }
        ]
    }
    requests.post(error_notice_webhook_url, json.dumps(error_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿


@client3.event
async def on_ready():
    try:
        loop.start()
        login_notice_ch = client3.get_channel(597978849476870153)
        with open("./datas/version.txt", mode="r", encoding="utf-8") as f:
            version = f.read()
        await login_notice_ch.send(f"{client3.user.name}がログインしました(from: {where_from})\n{os.path.basename(__file__)}により起動\nversion: {version}")

    except:
        unexpected_error()


@client3.event
async def on_message(message):
    if message.content == ">bot_stop":
        if message.guild is None:
            await message.channel.send("このコマンドはけいの実験サーバでのみ使用可能です")
            return
        kei_ex_guild = client3.get_guild(585998962050203672)
        if message.guild != kei_ex_guild:
            await message.channel.send("このコマンドはけいの実験サーバでのみ使用可能です")
            return
        can_bot_stop_role = kei_ex_guild.get_role(707570554462273537)
        if not can_bot_stop_role in message.author.roles:
            await message.channel.send("何様のつもり？")
            doM_role = message.guild.get_role(616212704818102275)
            await message.author.add_roles(doM_role)
            return

        await client3.close()
        now = datetime.datetime.now().strftime(r"%Y年%m月%d日　%H:%M")
        stop_msg = f"{message.author.mention}により{client3.user.name}が停止させられました"
        main_content = {
            "username": "BOT STOP",
            "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
            "content": "<@523303776120209408>",
            "embeds": [
                {
                    "title": "botが停止させられました",
                    "description": stop_msg,
                    "color": 0xff0000,
                    "footer": {
                        "text": now
                    }
                }
            ]
        }
        requests.post(error_notice_webhook_url, json.dumps(main_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿
        return

    if client3.user in message.mentions:
        await message.channel.send(f"{where_from}\n{os.path.basename(__file__)}")

    try:
        if message.content.startswith("//") or (message.clean_content.startswith("/*") and message.clean_content.endswith("*/")):
            return

        if message.guild is None: #DMでは反応しない
            return

        if message.content == ">help":
            await help(message)

        if not message.channel.id == 691901316133290035: #ミニゲーム
        #if not message.channel.id == 597978849476870153: #3組
            return

        if message.content.startswith(">ox"):
            await start_ox(message)

        elif message.content.startswith(">othello"):
            await start_othello(message)

        elif message.content == ">syogi":
            await start_syogi(message)

        elif message.content == ">uno":
            await start_uno(message)

        elif message.content == ">quoridor":
            await start_quoridor(message)

        elif message.content == ">contrast":
            await start_contrast(message)

        elif message.content.startswith(">mattix"):
            await start_mattix(message)

        elif message.content == ">puzzle15":
            await start_puzzle15(message)

        elif message.content == ">cancel":
            await cancel(message)

    except:
        unexpected_error()


def is_you_entry_game(message):
    if any(
        (
            message.author in about_ox,
            message.author in about_othello,
            message.author in about_syogi,
            message.author in about_uno,
            message.author in about_quoridor,
            message.author in about_contrast,
            message.author in about_mattix,
            message.author in about_puzzle15
        )
    ):
        return False
    else:   
        return True


async def start_ox(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return

    if len(about_ox) == 3: #先に募集している人がいたら
        if message.content == ">ox":
            now_playing = True
            about_ox.append(message.author)
            await message.channel.send("勝負を開始します！")
            await ox.match_ox(client3, message, about_ox)
            now_playing = False

        else:
            size = about_ox[1]
            await message.channel.send(f"現在{about_ox[2].name}さんが{size}×{size}で募集しています\n参加する場合`>ox`と入力してください")
            return

    else: #募集をかける立場なら
        try:
            size = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("引数は3~9の半角数字です")
            return

        if size < 3 or size > 9:
            await message.channel.send("引数は3~9の半角数字です")
            return

        about_ox.append(datetime.datetime.now())
        about_ox.append(size)
        about_ox.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>ox`で参加")


async def start_othello(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return

    if len(about_othello) == 3: #先に募集している人がいたら
        if message.content == ">othello":
            now_playing = True
            about_othello.append(message.author)
            await message.channel.send("勝負を開始します！")
            await othello.match_othello(client3, message, about_othello)
            now_playing = False

        else:
            size = about_othello[1]
            await message.channel.send(f"現在{about_othello[2].name}さんが{size}×{size}で募集しています\n参加する場合`>othello`と入力してください")
            return

    else: #募集をかける立場なら
        try:
            size = int(message.content.split()[1])
        except (IndexError, ValueError):
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        if size < 4 or size > 8:
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        if size % 2 == 1:
            await message.channel.send("引数は4~8の半角数字で偶数です")
            return

        about_othello.append(datetime.datetime.now())
        about_othello.append(size)
        about_othello.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>othello`で参加")


async def start_syogi(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return

    if len(about_syogi) == 2: #先に募集している人がいたら
        now_playing = True
        about_syogi.append(message.author)
        await message.channel.send("勝負を開始します！")
        await syogi.match_syogi(client3, message, about_syogi)
        now_playing = False

    else: #募集をかける立場なら
        about_syogi.append(datetime.datetime.now())
        about_syogi.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>syogi`で参加")


async def start_uno(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return

    if len(about_uno) == 0:
        about_uno.append(datetime.datetime.now())
        embed = discord.Embed(
            title="UNO募集",
            description=f"{message.author.mention}",
            color=random.choice([0x0000ff, 0x00aa00, 0xff0000, 0xffff00])
        )
        msg = await message.channel.send(content="✋で参加、👋で退出、🆗で開始\n・UNOコール不要\n・ドローに重ねての回避不可\n・記号カードで上がれる\n・ドロー4のチャレンジなし```\nワイルド→WL, ドロー4→D4, 山札から引く→PL, その他→カードに記載```リアクションが全て付いてからアクションを行ってください\nメッセージ系タイムアウト1分, リアクション系タイムアウト30秒", embed=embed)
        about_uno.append(msg)
        await msg.add_reaction("✋")
        await msg.add_reaction("👋")
        await msg.add_reaction("🆗")

        about_uno.append(False) #プレイ中のフラグ
        about_uno.append(message.author)

    elif not about_uno[2]: #募集中なら
        await message.channel.send(f"現在{about_uno[3].name}により募集されています")
        return


async def start_quoridor(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return
    
    if len(about_quoridor) == 2: #先に募集している人がいたら
        now_playing = True
        about_quoridor.append(message.author)
        await message.channel.send("勝負を開始します！")
        await quoridor.match_quoridor(client3, message, about_quoridor)
        now_playing = False

    else: #募集をかける立場なら
        about_quoridor.append(datetime.datetime.now())
        about_quoridor.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>quoridor`で参加")


async def start_contrast(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return
    
    if len(about_contrast) == 2: #先に募集している人がいたら
        now_playing = True
        about_contrast.append(message.author)
        await message.channel.send("勝負を開始します！")
        await contrast.match_contrast(client3, message, about_contrast)
        now_playing = False

    else: #募集をかける立場なら
        about_contrast.append(datetime.datetime.now())
        about_contrast.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>contrast`で参加")


async def start_mattix(message):
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return
    
    if len(about_mattix) == 3: #先に募集している人がいたら
        now_playing = True
        about_mattix.append(message.author)
        await message.channel.send("勝負を開始します！")
        await mattix.match_mattix(client3, message, about_mattix)
        now_playing = False

    else:
        try:
            mode = message.content.split()[1]
        except IndexError:
            await message.channel.send("type `>mattix` basic or `>mattix` advance")
            return
        
        if mode.lower() not in ("basic", "advance"):
            await message.channel.send("type `>mattix` basic or `>mattix` advance")
            return

        about_mattix.append(datetime.datetime.now())
        about_mattix.append(mode)
        about_mattix.append(message.author)
        await message.channel.send("他の参加者を待っています・・・\n他の参加者: `>mattix`で参加")


async def start_puzzle15(message):
    await message.channel.send("このゲームは未完成です。実装をお待ちください。")
    return
    global now_playing
    if now_playing:
        await message.channel.send("現在プレイ中です。しばらくお待ちください。")
        return

    if not is_you_entry_game(message):
        await message.channel.send("あなたは既に募集しているかプレイ中のため募集・参加できません")
        return


async def cancel(message):
    if message.author in about_ox:
        if len(about_ox) == 4: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return

        about_ox.clear()
        await message.channel.send("募集をキャンセルしました")

    elif message.author in about_othello:
        if len(about_othello) == 4: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return

        about_othello.clear()
        await message.channel.send("募集をキャンセルしました")

    elif message.author in about_syogi:
        if len(about_othello) == 3: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return

        about_syogi.clear()
        await message.channel.send("募集をキャンセルしました")

    elif message.author in about_quoridor:
        if len(about_quoridor) == 4: #勝負中なら
            await message.channel.send("勝負中は抜けられません")
            return

        about_quoridor.clear()
        await message.channel.send("募集をキャンセルしました")
    
    elif message.author in about_uno:
        if about_uno[2]:
            await message.channel.send("勝負中は抜けられません")
            return

        await message.channel.send("UNOへの参加キャンセルはリアクションで行ってください")

    elif message.author in about_contrast:
        if len(about_contrast) == 3:
            await message.channel.send("勝負中は抜けられません")
            return
        
        about_contrast.clear()
        await message.channel.send("募集をキャンセルしました")

    elif message.author in about_mattix:
        if len(about_mattix) == 3:
            await message.channel.send("勝負中は抜けられません")
            return
        
        about_mattix.clear()
        await message.channel.send("募集をキャンセルしました")

    elif message.author in about_puzzle15:
        await message.channel.send("1分間放置するとタイムアウトします")

    else:
        await message.channel.send("あなたは募集を行っていません")


async def help(message):
    help_embed = discord.Embed(
        title=f"{client3.user.name}のヘルプ",
        color=0xd00000
    )

    description = (
        "```\n"
        ">ox n     : n×nの○×ゲームを募集します(3≦n≦9)\n"
        ">ox       : 募集されている○×ゲームに参加します\n"
        ">othello n: n×nのオセロを募集します(n=4, 6, 8)\n"
        ">othello  : 募集されているオセロに参加します\n"
        ">syogi    : 将棋を募集・参加します\n"
        ">uno      : UNOを募集します\n"
        ">quoridor : コリドールを募集・参加します\n"
        ">contrast : コントラストを募集・参加します\n"
        ">puzzle15 : 15パズルを開始します(1人用)```"
    )
    help_embed.add_field(name="コマンド一覧", value=description, inline=False)
    await message.channel.send(embed=help_embed)


@client3.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if len(about_uno) == 0:
        return

    if about_uno[2]:
        return

    if reaction.message == about_uno[1]:
        msg = about_uno[1]
        player = reaction.message.guild.get_member(user.id)
        if reaction.emoji == "✋":
            if player in about_uno:
                await reaction.remove(user)
                return
            about_uno.append(player)
            description = ""
            for mem in about_uno[3:]:
                description += f"{mem.mention}\n"
            embed = discord.Embed(
                title="UNO募集",
                description=description,
                color=msg.embeds[0].color
            )
            await msg.edit(embed=embed)
            await reaction.remove(user)
        elif reaction.emoji == "👋":
            if not (player in about_uno):
                await reaction.remove(user)
                return
            about_uno.remove(player)
            if len(about_uno[3:]) == 0:
                embed = discord.Embed(
                    title="募集終了",
                    description="参加者が全員退出したため募集は終了されました",
                    color=0x000000
                )
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                about_uno.clear()
                return
            description = ""
            for mem in about_uno[3:]:
                description += f"{mem.mention}\n"
            embed = discord.Embed(
                title="UNO募集",
                description=description,
                color=msg.embeds[0].color
            )
            await msg.edit(embed=embed)
            await reaction.remove(user)
        elif reaction.emoji == "🆗":
            if not(player in about_uno):
                await reaction.remove(user)
                return
            if len(about_uno[3:]) == 1:
                await msg.channel.send("1人でUNOする気ですか？させませんよ", delete_after=3)
                await reaction.remove(user)
                return
            description = ""
            for mem in about_uno[3:]:
                description += f"{mem.mention}\n"
            about_uno[2] = True
            embed = discord.Embed(
                title="**募集終了**",
                description=description,
                color=msg.embeds[0].color
            )
            await msg.edit(content=f"{user.name}がゲームを開始しました", embed=embed)
            await msg.clear_reactions()
            await uno.match_uno(client3, msg, about_uno)
        else:
            await reaction.remove(user)


@tasks.loop(seconds=60)
async def loop():
    await client3.wait_until_ready()

    before_30min = datetime.datetime.now() - datetime.timedelta(minutes=30)
    ch = client3.get_channel(691901316133290035) #ミニゲーム
    #ch = client3.get_channel(597978849476870153) #3組
    if len(about_ox) == 3:
        if about_ox[1] <= before_30min:
            member = about_ox[2]
            about_ox.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_othello) == 3:
        if about_othello[1] <= before_30min:
            member = about_othello[2]
            about_othello.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_syogi) == 2:
        if about_syogi[0] <= before_30min:
            member = about_syogi[1]
            about_syogi.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_uno) == 4:
        if about_uno[0] <= before_30min:
            about_uno.clear()
            await ch.send("30分間参加がなかったので募集は取り消されました")

    if len(about_quoridor) == 2:
        if about_quoridor[0] <= before_30min:
            member = about_quoridor[1]
            about_quoridor.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")

    if len(about_contrast) == 2:
        if about_contrast[0] <= before_30min:
            member = about_contrast[1]
            about_contrast.clear()
            await ch.send(f"{member.mention}\n30分間参加がなかったので募集は取り消されました")


client3.run(os.getenv("discord_bot_token_3"))