import asyncio
import math
import random

import discord
from PIL import Image

bahuda = None
win_number = 1
reverse = False

def create_pic_uno(match, player_number=None):
	if player_number is None:
		player_number = 0
		for player_cards in match[:len(match)-1]:
			dansuu = math.ceil(len(player_cards) / 10)
			uno = Image.new(mode="RGB", size=(350, dansuu*70), color=0x3f3936)
			for i in range(dansuu):
				retsusuu = 0
				for card in player_cards:
					image = Image.open(f"./uno/{card}.png")
					uno.paste(image, (retsusuu*50, i*70))
					retsusuu += 1
			uno.save(f"./game_pic/uno_player{player_number}.png")
			player_number += 1

	else:
		player_cards = match[player_number]
		dansuu = math.ceil(len(player_cards) / 10)
		if dansuu == 1:
			maisuu = len(player_cards)
			uno = Image.new(mode="RGB", size=(maisuu*50, dansuu*70), color=0x3f3936)
		else:
			uno = Image.new(mode="RGB", size=(500, dansuu*70), color=0x3f3936)
		x = 0
		y = 0
		for card in player_cards:
			if x == 10:
				x = 0
				y += 1
			if isinstance(card, str):
				image = Image.open(f"./uno/{card}.png")
				uno.paste(image, (x*50, y*70))
			x += 1
		uno.save(f"./game_pic/uno_player{player_number}.png")
		

def who_is_higaisya(match, player_number, player_list):
	if not reverse:
		higaisya_number = player_number + 1
		if higaisya_number == len(player_list):
			higaisya_number = 0
		while True:
			if isinstance(match[higaisya_number][0], str):
				break
			else:
				higaisya_number += 1
				if higaisya_number == len(player_list):
					higaisya_number = 0
	else:
		higaisya_number = player_number - 1
		if higaisya_number == -1:
			higaisya_number = len(player_list) - 1
		while True:
			if isinstance(match[higaisya_number][0], str):
				break
			else:
				higaisya_number -= 1
				if higaisya_number == -1:
					higaisya_number = len(player_list) - 1

	return higaisya_number


def check_finish(match, player, player_list, player_number): #発火されるのは手持ちのカードを出した時(山札から引いたときは発火されない)
	global win_number
	if len(match[player_number]) == 0: #手持ちのカードの残りが0になった時
		match[player_number].clear()
		match[player_number].append(win_number)
		match[player_number].append(player)
		match[player_number].append(0)
		win_number += 1

		not_finish_counter = 0 #まだ上がってないプレイヤー数
		player_num = 0 #チェック済みのプレイヤー番号
		for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
			if isinstance(player_cards[0], str):
				not_finish_player = player_list[player_num]
				not_finish_counter += 1
			player_num += 1
		if not_finish_counter == 1:
			not_finish_player_number = player_list.index(not_finish_player)
			remaining = len(match[not_finish_player_number])
			match[not_finish_player_number].clear()
			match[not_finish_player_number].append(win_number)
			match[not_finish_player_number].append(not_finish_player)
			match[not_finish_player_number].append(remaining)
			return (match, True)

	return (match, False)


def who_is_next(match, player_number, player_list):
	global reverse
	if not reverse:
		player_number += 1
		if player_number == len(player_list):
			player_number = 0
		while True:
			if isinstance(match[player_number][0], int):
				player_number += 1
				if player_number == len(player_list):
					player_number = 0
			else:
				break

	else:
		player_number -= 1
		if player_number == -1:
			player_number = len(player_list) - 1
		while True:
			if isinstance(match[player_number][0], int):
				player_number -= 1
				if player_number == -1:
					player_number = len(player_list) - 1
			else:
				break

	return player_number


async def pull_card(match, client3, message, player, player_list, player_number, timeout, finish):
	global bahuda
	match[player_number].append(match[-1][0])
	hiita_card = match[-1][0]
	del match[-1][0]
	match = match
	if hiita_card in ("WL", "D4") or hiita_card[0] == bahuda[0] or hiita_card[1] == bahuda[1]: #引いたカードが出せる状態なら
		create_pic_uno(match, player_number)
		f = discord.File(f"./game_pic/uno_player{player_number}.png")
		msg = await player.send(content=f"{hiita_card}を引きました。使いますか？", file=f)
		await msg.add_reaction("👍")
		await msg.add_reaction("👎")

		def check2(reaction, user):
			return user.id == player.id and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")

		try:
			reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
		except asyncio.TimeoutError:
			remaining = len(match[player_number])
			match[player_number].clear()
			match[player_number].append(lose_number)
			match[player_number].append(player)
			match[player_number].append(remaining)
			lose_number -= 1
			timeout = True
			await message.channel.send(f"{player.name}さんがタイムアウトしました")
			for p in player_list:
				await p.send(f"{player.name}さんがタイムアウトしました")
			not_finish_counter = 0 #まだ上がってないプレイヤー数
			player_num = 0 #チェック済みのプレイヤー番号
			for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
				if isinstance(player_cards[0], str):
					not_finish_player = player_list[player_num]
					not_finish_counter += 1
				player_num += 1
			if not_finish_counter == 1:
				not_finish_player_number = player_list.index(not_finish_player)
				match[not_finish_player_number].clear()
				match[not_finish_player_number].append(win_number)
				match[not_finish_player_number].append(not_finish_player)
				finish = True

			return timeout, finish

		if str(reaction.emoji) == "👍":
			if hiita_card == "WL":
				msg = await player.send("何色にしますか？")
				for reaction in ("🟦", "🟩", "🟥", "🟨"):
					await msg.add_reaction(reaction)
				def check2(reaction, user):
					return user.id == player.id and (str(reaction.emoji) == "🟦" or str(reaction.emoji) == "🟩" or str(reaction.emoji) == "🟥" or str(reaction.emoji) == "🟨")
				try:
					reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
				except asyncio.TimeoutError:
					remaining = len(match[player_number])
					match[player_number].clear()
					match[player_number].append(lose_number)
					match[player_number].append(player)
					match[player_number].append(remaining)
					lose_number -= 1
					timeout = True
					await message.channel.send(f"{player.name}さんがタイムアウトしました")
					for p in player_list:
						await p.send(f"{player.name}さんがタイムアウトしました")
					not_finish_counter = 0 #まだ上がってないプレイヤー数
					player_num = 0 #チェック済みのプレイヤー番号
					for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
						if isinstance(player_cards[0], str):
							not_finish_player = player_list[player_num]
							not_finish_counter += 1
						player_num += 1
					if not_finish_counter == 1:
						not_finish_player_number = player_list.index(not_finish_player)
						match[not_finish_player_number].clear()
						match[not_finish_player_number].append(win_number)
						match[not_finish_player_number].append(not_finish_player)
						finish = True

					return timeout, finish

				if str(reaction.emoji) == "🟦":
					bahuda = "BW"
					color = "青🟦"
				elif str(reaction.emoji) == "🟩":
					bahuda = "GW"
					color = "緑🟩"
				elif str(reaction.emoji) == "🟥":
					bahuda = "RW"
					color = "赤🟥"
				elif str(reaction.emoji) == "🟨":
					bahuda = "YW"
					color = "黄🟨"
				match[player_number].remove(hiita_card)
				match = match
				create_pic_uno(match, player_number)
				remaining = len(match[player_number])
				f = discord.File(f"./uno/{bahuda}.png")
				await message.channel.send(content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚", file=f)
				for p in player_list:
					if p == player:
						f = discord.File(f"./game_pic/uno_player{player_number}.png")
						await p.send(content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚", file=f)
					else:
						f = discord.File(f"./uno/{bahuda}.png")
						await p.send(content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚", file=f)

			elif hiita_card == "D4":
				msg = await player.send("何色にしますか？")
				for reaction in ("🟦", "🟩", "🟥", "🟨"):
					await msg.add_reaction(reaction)
				def check2(reaction, user):
					return user.id == player.id and (str(reaction.emoji) == "🟦" or str(reaction.emoji) == "🟩" or str(reaction.emoji) == "🟥" or str(reaction.emoji) == "🟨")
				try:
					reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
				except asyncio.TimeoutError:
					remaining = len(match[player_number])
					match[player_number].clear()
					match[player_number].append(lose_number)
					match[player_number].append(player)
					match[player_number].append(remaining)
					lose_number -= 1
					timeout = True
					await message.channel.send(f"{player.name}さんがタイムアウトしました")
					for p in player_list:
						await p.send(f"{player.name}さんがタイムアウトしました")
					not_finish_counter = 0 #まだ上がってないプレイヤー数
					player_num = 0 #チェック済みのプレイヤー番号
					for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
						if isinstance(player_cards[0], str):
							not_finish_player = player_list[player_num]
							not_finish_counter += 1
						player_num += 1
					if not_finish_counter == 1:
						not_finish_player_number = player_list.index(not_finish_player)
						match[not_finish_player_number].clear()
						match[not_finish_player_number].append(win_number)
						match[not_finish_player_number].append(not_finish_player)
						finish = True

					return timeout, finish

				if str(reaction.emoji) == "🟦":
					bahuda = "BA"
					color = "青🟦"
				elif str(reaction.emoji) == "🟩":
					bahuda = "GA"
					color = "緑🟩"
				elif str(reaction.emoji) == "🟥":
					bahuda = "RA"
					color = "赤🟥"
				elif str(reaction.emoji) == "🟨":
					bahuda = "YA"
					color = "黄🟨"
				match[player_number].remove(hiita_card)
				remaining = len(match[player_number])
				higaisya_number = who_is_higaisya(match, player_number, player_list)
				match[higaisya_number] += match[-1][0:4]
				del match[-1][0:4]
				match = match
				create_pic_uno(match, player_number)
				create_pic_uno(match, higaisya_number)
				higaisya = player_list[higaisya_number]
				higaisya_remaining = len(match[higaisya_number])
				f = discord.File(f"./uno/{bahuda}.png")
				await message.channel.send(
					content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
					file=f
				)
				for p in player_list:
					if p == player:
						f = discord.File(f"./game_pic/uno_player{player_number}.png")
						await p.send(
							content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
							file=f
						)
					elif p == higaisya:
						f = discord.File(f"./game_pic/uno_player{higaisya_number}.png")
						await p.send(
							content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
							file=f
						)
					else:
						f = discord.File(f"./uno/{bahuda}.png")
						await p.send(
							content=f"{player.name}さんは山札から{hiita_card}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
							file=f
						)

				player_number = who_is_next(match, player_number, player_list)

			elif hiita_card[0] == bahuda[0] or hiita_card[1] == bahuda[1]:
				bahuda = hiita_card
				match[player_number].remove(hiita_card)
				remaining = len(match[player_number])
				create_pic_uno(match, player_number)
				if hiita_card[1] == "D":
					higaisya_number = who_is_higaisya(match, player_number, player_list)
					match[higaisya_number] += match[-1][0:2]
					del match[-1][0:2]
					match = match
					create_pic_uno(match, higaisya_number)
					higaisya = player_list[higaisya_number]
					higaisya_remaining = len(match[higaisya_number])
					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(
						content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
						file=f
					)
					for p in player_list:
						if p == player:
							f = discord.File(f"./game_pic/uno_player{player_number}.png")
							await p.send(
								content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
								file=f
							)
						elif p == higaisya:
							f = discord.File(f"./game_pic/uno_player{higaisya_number}.png")
							await p.send(
								content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
								file=f
							)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(
								content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
								file=f
							)

					player_number = who_is_next(match, player_number, player_list)

				elif hiita_card[1] == "R":
					if not reverse:
						reverse = True
					else:
						reverse = False

					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)
					for p in player_list:
						if p == player:
							f = discord.File(f"./game_pic/uno_player{player_number}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)

				elif hiita_card[1] == "S":
					skiped_player_number = who_is_higaisya(match, player_number, player_list)
					skiped_player = player_list[skiped_player_number]

					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)
					for p in player_list:
						if p == player:
							f = discord.File(f"./game_pic/uno_player{player_number}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)
						elif p == skiped_player:
							f = f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\nあなたは飛ばされました。", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)

					player_number = skiped_player_number

				else:
					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚", file=f)
					for p in player_list:
						if p == player:
							f = discord.File(f"./game_pic/uno_player{player_number}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは山札から{hiita_card}を出しました。残り{remaining}枚", file=f)

			return timeout, finish

	create_pic_uno(match, player_number)
	remaining = len(match[player_number])
	await message.channel.send(content=f"{player.name}さんは山札から引きました。残り{remaining}枚")
	for p in player_list:
		if p == player:
			f = discord.File(f"./game_pic/uno_player{player_number}.png")
			await p.send(content=f"{hiita_card}を引きました", file=f)
		else:
			await p.send(content=f"{player.name}さんは山札から引きました。残り{remaining}枚")

	return timeout, finish


async def wild_card(match, client3, message, player, player_list, player_number, timeout, finish):
	global bahuda
	content = "WL"
	msg = await player.send("何色にしますか？")
	for reaction in ("🟦", "🟩", "🟥", "🟨"):
		await msg.add_reaction(reaction)

	def check2(reaction, user):
		return user.id == player.id and (str(reaction.emoji) == "🟦" or str(reaction.emoji) == "🟩" or str(reaction.emoji) == "🟥" or str(reaction.emoji) == "🟨")

	try:
		reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
	except asyncio.TimeoutError:
		remaining = len(match[player_number])
		match[player_number].clear()
		match[player_number].append(lose_number)
		match[player_number].append(player)
		match[player_number].append(remaining)
		lose_number -= 1
		timeout = True
		await message.channel.send(f"{player.name}さんがタイムアウトしました")
		for p in player_list:
			await p.send(f"{player.name}さんがタイムアウトしました")
		not_finish_counter = 0 #まだ上がってないプレイヤー数
		player_num = 0 #チェック済みのプレイヤー番号
		for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
			if isinstance(player_cards[0], str):
				not_finish_player = player_list[player_num]
				not_finish_counter += 1
			player_num += 1
		if not_finish_counter == 1:
			not_finish_player_number = player_list.index(not_finish_player)
			match[not_finish_player_number].clear()
			match[not_finish_player_number].append(win_number)
			match[not_finish_player_number].append(not_finish_player)
			finish = True

		return timeout, finish

	if str(reaction.emoji) == "🟦":
		bahuda = "BW"
		color = "青🟦"
	elif str(reaction.emoji) == "🟩":
		bahuda = "GW"
		color = "緑🟩"
	elif str(reaction.emoji) == "🟥":
		bahuda = "RW"
		color = "赤🟥"
	elif str(reaction.emoji) == "🟨":
		bahuda = "YW"
		color = "黄🟨"
	match[player_number].remove(content)
	match, finish = check_finish(match, player, player_list, player_number)
	create_pic_uno(match, player_number)
	remaining = len(match[player_number])
	if isinstance(match[player_number][0], int):
		remaining = 0
	f = discord.File(f"./uno/{bahuda}.png")
	await message.channel.send(content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚", file=f)
	for p in player_list:
		if p == player:
			if remaining == 0:
				await p.send(content=f"{player.name}さんは{content}を出し{color}に設定し上がりました。")
			else:
				f = discord.File(f"./game_pic/uno_player{player_number}.png")
				await p.send(content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚", file=f)
		else:
			f = discord.File(f"./uno/{bahuda}.png")
			await p.send(content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚", file=f)

	return timeout, finish


async def drow_4(match, client3, message, player, player_list, player_number, timeout, finish):
	global bahuda
	content = "D4"
	msg = await player.send("何色にしますか？")
	for reaction in ("🟦", "🟩", "🟥", "🟨"):
		await msg.add_reaction(reaction)
	def check2(reaction, user):
		return user.id == player.id and (str(reaction.emoji) == "🟦" or str(reaction.emoji) == "🟩" or str(reaction.emoji) == "🟥" or str(reaction.emoji) == "🟨")
	try:
		reaction, user = await client3.wait_for("reaction_add", check=check2, timeout=30)
	except asyncio.TimeoutError:
		remaining = len(match[player_number])
		match[player_number].clear()
		match[player_number].append(lose_number)
		match[player_number].append(player)
		match[player_number].append(remaining)
		lose_number -= 1
		timeout = True
		await message.channel.send(f"{player.name}さんがタイムアウトしました")
		for p in player_list:
			await p.send(f"{player.name}さんがタイムアウトしました")
		not_finish_counter = 0 #まだ上がってないプレイヤー数
		player_num = 0 #チェック済みのプレイヤー番号
		for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
			if isinstance(player_cards[0], str):
				not_finish_player = player_list[player_num]
				not_finish_counter += 1
			player_num += 1
		if not_finish_counter == 1:
			not_finish_player_number = player_list.index(not_finish_player)
			match[not_finish_player_number].clear()
			match[not_finish_player_number].append(win_number)
			match[not_finish_player_number].append(not_finish_player)
			finish = True

		return timeout, finish

	if str(reaction.emoji) == "🟦":
		bahuda = "BA"
		color = "青🟦"
	elif str(reaction.emoji) == "🟩":
		bahuda = "GA"
		color = "緑🟩"
	elif str(reaction.emoji) == "🟥":
		bahuda = "RA"
		color = "赤🟥"
	elif str(reaction.emoji) == "🟨":
		bahuda = "YA"
		color = "黄🟨"
	match[player_number].remove(content)
	match, finish = check_finish(match, player, player_list, player_number)
	remaining = len(match[player_number])
	if isinstance(match[player_number][0], int):
		remaining = 0
	higaisya_number = who_is_higaisya(match, player_number, player_list)
	match[higaisya_number] += match[-1][0:4]
	del match[-1][0:4]
	match = match
	create_pic_uno(match, player_number)
	create_pic_uno(match, higaisya_number)
	higaisya = player_list[higaisya_number]
	higaisya_remaining = len(match[higaisya_number])
	f = discord.File(f"./uno/{bahuda}.png")
	await message.channel.send(
		content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
		file=f
	)
	for p in player_list:
		if p == player:
			if remaining == 0:
				await p.send(content=f"{player.name}さんは{content}を出し{color}に設定し上がりました。\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}")
			else:
				f = discord.File(f"./game_pic/uno_player{player_number}.png")
				await p.send(
					content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
					file=f
				)
		elif p == higaisya:
			f = discord.File(f"./game_pic/uno_player{higaisya_number}.png")
			await p.send(
				content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
				file=f
			)
		else:
			f = discord.File(f"./uno/{bahuda}.png")
			await p.send(
				content=f"{player.name}さんは{content}を出し{color}に設定しました。残り{remaining}枚\n{higaisya.name}さんに4ダメージ！！残り{higaisya_remaining}",
				file=f
			)

	player_number = who_is_next(match, player_number, player_list)
	return timeout, finish


async def match_uno(client3, message, about_uno):
	cards = [
		"B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "BS", "BD", "BR",
		"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "BS", "BD", "BR",
		"G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "GS", "GD", "GR",
		"G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "GS", "GD", "GR",
		"R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "RS", "RD", "RR",
		"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "RS", "RD", "RR",
		"Y0", "Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "YS", "YD", "YR",
		"Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "YS", "YD", "YR",
		"D4", "D4", "D4", "D4", "WL", "WL", "WL", "WL"
	]

	#match -> [[プレイヤーカード]×参加者数, [山札]]
	cards = random.sample(cards, k=108)
	player_list = about_uno[3:]
	match = []
	for player in player_list: #playerはdiscord.Member型
		player_cards = cards[0:7]
		match.append(player_cards)
		del cards[0:7]
		cards = cards

	match.append(cards) #match[-1]が山札

	create_pic_uno(match)

	player_number = 0
	cannot = False
	for player in player_list:
		f = discord.File(f"./game_pic/uno_player{player_number}.png")
		try:
			await player.send(file=f)
		except discord.errors.Forbidden:
			await message.channel.send(f"{player.mention}\nブロックを解除、またはDMの受信を許可してください")
			cannot = True
		player_number += 1

	if cannot:
		await message.channel.send("DMへの送信ができない人がいたためゲームを開始できませんでした")
		for p in player_list:
			await p.send(f"{message.channel.mention}\nDMへの送信ができない人がいたためゲームを開始できませんでした")
		about_uno.clear()
		return
	
	while True:
		bahuda = match[-1][0]
		if bahuda == "WL" or bahuda == "D4":
			match[-1].append(bahuda)
			del match[-1][0]
			match = match
		else:
			del match[-1][0]
			break

	f = discord.File(f"./uno/{bahuda}.png")
	await message.channel.send(content=f"{bahuda}でスタートです", file=f)
	for player in player_list:
		f = discord.File(f"./uno/{bahuda}.png")
		await player.send(content=f"{bahuda}でスタートです", file=f)
		player_number += 1

	global reverse
	global win_number
	player_number = 0
	lose_number = len(player_list)
	finish = False

	if bahuda[1] == "D":
		match[0] += match[-1][0:2]
		del match[-1][0:2]
		match = match
		create_pic_uno(match, 0)
		higaisya = player_list[0]
		higaisya_remaining = len(match[0])
		f = discord.File(f"./uno/{bahuda}.png")
		await message.channel.send(
			content=f"{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
			file=f
		)
		for p in player_list:
			if p == higaisya:
				f = discord.File("./game_pic/uno_player0.png")
				await p.send(
					content=f"{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
					file=f
				)
			else:
				f = discord.File(f"./uno/{bahuda}.png")
				await p.send(
					content=f"{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
					file=f
				)

		player_number = 1
		
	elif bahuda[1] == "R":
		reverse = True
		await message.channel.send(content=f"回り順が逆になります")
		for p in player_list:
			await p.send(content=f"回り順が逆になります")

		player_number = len(player_list) - 1

	elif bahuda[1] == "S":
		skiped_player = player_list[0]

		await message.channel.send(f"{skiped_player.name}さんが飛ばされました。")
		for p in player_list:
			if p == skiped_player:
				await p.send("あなたは飛ばされました。")
			else:
				await p.send(f"{skiped_player.name}さんが飛ばされました。")

		player_number = 1
		
	while True:
		player = player_list[player_number]
		if isinstance(match[player_number][0], int):
			continue

		create_pic_uno(match, player_number)
		await message.channel.send(content=f"{player.name}さんの番です")
		for p in player_list:
			if p == player:
				f = discord.File(f"./game_pic/uno_player{player_number}.png")
				await p.send(content=f"{player.name}さんの番です\nワイルド→WL, ドロー4→D4, 山札から引く→PL, その他→カードに記載", file=f)
			else:
				await p.send(content=f"{player.name}さんの番です")

		def check(m):
			if len(m.content) == 2:
				if m.author == player and (m.channel == message.channel or m.channel == player.dm_channel):
					return True
			return False

		timeout = False
		while True:
			try:
				reply = await client3.wait_for("message", check=check, timeout=60)
			except asyncio.TimeoutError:
				remaining = len(match[player_number])
				match[player_number].clear()
				match[player_number].append(lose_number)
				match[player_number].append(player)
				match[player_number].append(remaining)
				lose_number -= 1
				timeout = True
				await message.channel.send(f"{player.name}さんがタイムアウトしました")
				for p in player_list:
					await p.send(f"{player.name}さんがタイムアウトしました")
				not_finish_counter = 0 #まだ上がってないプレイヤー数
				player_num = 0 #チェック済みのプレイヤー番号
				for player_cards in match[:len(player_list)]: #上がっていない人数が何人いるか確認
					if isinstance(player_cards[0], str):
						not_finish_player = player_list[player_num]
						not_finish_counter += 1
					player_num += 1
				if not_finish_counter == 1:
					not_finish_player_number = player_list.index(not_finish_player)
					match[not_finish_player_number].clear()
					match[not_finish_player_number].append(win_number)
					match[not_finish_player_number].append(not_finish_player)
					finish = True

				continue

			content = reply.content.upper()
			if not (content in match[player_number] or content == "PL"):
				await player.send("あなたはそのカードを持っていません")
				continue

			if content == "PL":
				timeout, finish = await pull_card(match, client3, message, player, player_list, player_number, timeout, finish)

			elif content == "WL":
				timeout, finish = await wild_card(match, client3, message, player, player_list, player_number, timeout, finish)

			elif content == "D4":
				timeout, finish = await drow_4(match, client3, message, player, player_list, player_number, timeout, finish)

			elif content[0] == bahuda[0] or content[1] == bahuda[1]:
				bahuda = content
				match[player_number].remove(content)
				match, finish = check_finish(match, player, player_list, player_number)
				remaining = len(match[player_number])
				if isinstance(match[player_number][0], int):
						remaining = 0
				create_pic_uno(match, player_number)
				if content[1] == "D":
					higaisya_number = who_is_higaisya(match, player_number, player_list)
					match[higaisya_number] += match[-1][0:2]
					del match[-1][0:2]
					match = match
					create_pic_uno(match, higaisya_number)
					higaisya = player_list[higaisya_number]
					higaisya_remaining = len(match[higaisya_number])
					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(
						content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
						file=f
					)
					for p in player_list:
						if p == player:
							if remaining == 0:
								await p.send(content=f"{player.name}さんは{content}を出し上がりました。\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}")
							else:
								f = discord.File(f"./game_pic/uno_player{player_number}.png")
								await p.send(
									content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
									file=f
								)
						elif p == higaisya:
							f = discord.File(f"./game_pic/uno_player{higaisya_number}.png")
							await p.send(
								content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
								file=f
							)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(
								content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{higaisya.name}さんに2ダメージ！！残り{higaisya_remaining}",
								file=f
							)

					player_number = who_is_next(match, player_number, player_list)
				
				elif content[1] == "R":
					if not reverse:
						reverse = True
					else:
						reverse = False

					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)
					for p in player_list:
						if p == player:
							if remaining == 0:
								await p.send(content=f"{player.name}さんは{content}を出し上がりました。残り{remaining}枚\n回り順が逆になります")
							else:
								f = discord.File(f"./game_pic/uno_player{player_number}.png")
								await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n回り順が逆になります", file=f)

				elif content[1] == "S":
					skiped_player_number = who_is_higaisya(match, player_number, player_list)
					skiped_player = player_list[skiped_player_number]

					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)
					for p in player_list:
						if p == player:
							if remaining == 0:
								await p.send(content=f"{player.name}さんは{content}を出し上がりました。\n{skiped_player.name}さんが飛ばされました。")
							else:
								f = discord.File(f"./game_pic/uno_player{player_number}.png")
								await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)
						elif p == skiped_player:
							f = f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\nあなたは飛ばされました。", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚\n{skiped_player.name}さんが飛ばされました。", file=f)

					player_number = skiped_player_number

				else:
					f = discord.File(f"./uno/{bahuda}.png")
					await message.channel.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚", file=f)
					for p in player_list:
						if p == player:
							if remaining == 0:
								await p.send(content=f"{player.name}さんは{content}を出し上がりました。")
							else:
								f = discord.File(f"./game_pic/uno_player{player_number}.png")
								await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚", file=f)
						else:
							f = discord.File(f"./uno/{bahuda}.png")
							await p.send(content=f"{player.name}さんは{content}を出しました。残り{remaining}枚", file=f)

			else:
				await player.send(f"そのカードは出せません\n現在の場札: {bahuda}\nもう一度入力してください")
				continue
			
			break

		if finish:
			break

		if timeout:
			break

		player_number = who_is_next(match, player_number, player_list)

	#finish が Trueならここが実行される
	play_data = match[:len(player_list)]
	play_data = sorted(play_data, key=lambda x: -x[0], reverse=True)
	description = ""
	for data in play_data:
		if data[2] == 0:
			remaining = ""
		else:
			remaining = f": {data[2]}枚"
		description += f"{data[0]}位: {data[1].name}{remaining}\n"
	embed = discord.Embed(
		title="結果発表",
		description=description,
		color=message.embeds[0].color
	)
	await message.channel.send(embed=embed)
	for p in player_list:
		await p.send(content=f"{message.channel.mention}", embed=embed)
	bahuda = None
	win_number = 1
	reverse = False
	about_uno.clear()