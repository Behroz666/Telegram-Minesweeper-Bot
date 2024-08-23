import random
import copy
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

data = {}

description = """Minesweeper: Overview and How to Play

Objective:  
The goal of Minesweeper is to clear a grid of hidden mines without detonating any. The numbers revealed on the grid indicate how many mines are adjacent to that square, helping you deduce where the mines are hidden.

How to Play:
   - Use /start to start new game
   - The first click will definitely reveal a number or an empty space. An empty space indicates no adjacent mines. 
   - Each number on a revealed square shows how many mines are adjacent to it (including diagonals). Use this information to figure out where the mines might be.
   - If you click on a mine, the game is over.
   - The game is won when all non-mine squares are revealed.
   - You can click on the Flag button bellow the game to mark mines (click again to remove flag) you can open cells by clicking on mine button

Tips:
- Start with corners or edges to get better information.
- If you're unsure, guess, but be cautious!
- The mine counter is based on number of your flags

Enjoy the challenge and improve your strategy with practice!"""

default_game = [
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️",
    "▫️","▫️","▫️","▫️","▫️","▫️","▫️","▫️"
    ]
all = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]
no_after = [8,16,24,32,40,48,56,64]
no_before = [1,9,17,25,33,41,49,57]

def emoji(game):
    emoji_map = {
        0: "➖",
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣"
    }
    for i in range(len(game)):
        game[i] = emoji_map.get(game[i], game[i])
    return(game)

def chunk(table):
    rows = []
    i = 1
    for n in no_after:
        row = table[n - 8:n]
        rows.append(row)
        i += 1
    return(rows)

def  make_keyboard(a):
    apart = chunk(emoji(a))
    keyboard = []
    for i in range(8):
        row = [
            InlineKeyboardButton(apart[i][j], callback_data=str(i * 8 + j + 1))
            for j in range(8)
        ]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💣", callback_data='bomb'),InlineKeyboardButton("🚩", callback_data='flag')])
    return(keyboard)

def  make_done_keyboard(a):
    apart = emoji(a)
    keyboard = [
        [InlineKeyboardButton(apart[i + j], callback_data='done') for j in range(8)]
        for i in range(0, len(apart), 8)
    ]
    return(keyboard)

def make_table(num, chat_id):
    global all
    number=[]
    number.append(num)
    data[chat_id]["bomb blocks"] = sorted(random.sample(list(set(all) - set(number)), 10))
    if num in data[chat_id]["bomb blocks"]:
        print("shit")
        for i in range(len(data[chat_id]["bomb blocks"])):
            if data[chat_id]["bomb blocks"][i] == num :
                data[chat_id]["bomb blocks"][i] = random.sample(list(set(all) - set(num)), 1)[0]
    table = []
    i = 1
    while i < 65:
        if i in data[chat_id]["bomb blocks"]:
            table.append("*")
        else:
            b = 0
            if i not in no_after and i not in no_before:
                if i + 1 in data[chat_id]["bomb blocks"]:
                    b += 1            
                if i - 1 in data[chat_id]["bomb blocks"]:
                    b += 1
                for num in [7,8,9]:
                    if i - num > 0 :
                        if i - num in data[chat_id]["bomb blocks"]:
                            b += 1
                    if i + num < 65 :
                        if i + num in data[chat_id]["bomb blocks"]:
                            b += 1
            elif i in no_after:
                if i - 1 in data[chat_id]["bomb blocks"]:
                    b += 1            
                if i - 8 > 0 and i - 8 in data[chat_id]["bomb blocks"] :
                    b += 1
                if i + 8 < 65 and i + 8 in data[chat_id]["bomb blocks"] :
                    b += 1            
                if i - 9 > 0 and i - 9 in data[chat_id]["bomb blocks"] :
                    b += 1
                if i + 7 < 65 and i + 7 in data[chat_id]["bomb blocks"] :
                    b += 1
            elif i in no_before:
                if i + 1 in data[chat_id]["bomb blocks"]:
                    b += 1            
                if i - 8 > 0 and i - 8 in data[chat_id]["bomb blocks"] :
                    b += 1
                if i + 8 < 65 and i + 8 in data[chat_id]["bomb blocks"] :
                    b += 1            
                if i - 7 > 0 and i - 7 in data[chat_id]["bomb blocks"] :
                    b += 1
                if i + 9 < 65 and i + 9 in data[chat_id]["bomb blocks"] :
                    b += 1
            table.append(b)
        i += 1
        continue
    return(table)

def counting(i):
    count = 10 - len(i)
    if count < 0 :
        more = abs(10 - len(i))
        count = f"You have found {more} more mine(s) than possible"
    return (count)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(description)    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global default_game
    chat_id = update.message.chat.id
    if chat_id not in data:
        data[chat_id] = {}
    data[chat_id]["time"] = time.time()
    data[chat_id]["flags"] = []
    data[chat_id]["opened"] = []
    data[chat_id]["bomb"] = True
    data[chat_id]["flag"] = False
    data[chat_id]["message id"] = update.message.message_id
    data[chat_id]["game"] = copy.deepcopy(default_game)
    data[chat_id]["checked"] = []
    counter = counting(data[chat_id]["flags"])
    await update.message.reply_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Mine mode 💣", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global no_after, no_before, all, default_game
    query = update.callback_query
    choice = query.data
    chat_id = query.from_user.id  
    query_data = query.message.message_id
    if query_data > data[chat_id]["message id"]:
        if data[chat_id]["game"] == default_game and choice in all:
            data[chat_id]["table"] = make_table(int(choice), chat_id)    
        if choice == "flag":
            if not data[chat_id]["flag"] : 
                counter = counting(data[chat_id]["flags"])
                await query.edit_message_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Flag mode 🚩", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))
            data[chat_id]["flag"] = True
            data[chat_id]["bomb"] = False
            await query.answer("Flag mode enabled")        
        elif choice == "bomb":
            if not data[chat_id]["bomb"]: 
                counter = counting(data[chat_id]["flags"])
                await query.edit_message_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Mine mode 💣", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))
            data[chat_id]["flag"] = False
            data[chat_id]["bomb"] = True
            await query.answer("Mine mode enabled")
        elif choice == "done":
            await query.answer("Your game is done. use /start")
        else: 
            choice = int(choice)
            if data[chat_id]["flag"]:
                if choice not in data[chat_id]["flags"] :
                    data[chat_id]["game"][choice - 1] = "🚩"
                    data[chat_id]["flags"].append(choice)
                    counter = counting(data[chat_id]["flags"])
                    await query.edit_message_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Flag mode 🚩", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))
                    await query.answer("Flag added")
                else:
                    data[chat_id]["game"][choice - 1] = "▫️"
                    data[chat_id]["flags"].remove(choice)
                    counter = counting(data[chat_id]["flags"])
                    await query.edit_message_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Flag mode 🚩", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))
                    await query.answer("Flag removed")
            elif data[chat_id]["bomb"]:
                if choice in data[chat_id]["flags"]:
                    await query.answer("It's Flag! you have to remove it fisrt")
                elif choice in data[chat_id]["opened"]:
                    await query.answer("Cell already openned")
                else: 
                    if choice in data[chat_id]["bomb blocks"]:
                        for i in data[chat_id]["bomb blocks"]:
                            data[chat_id]["game"][i-1] = "💣"
                        for i in data[chat_id]["flags"]:    
                            if data[chat_id]["game"][i-1] not in data[chat_id]["bomb blocks"]:
                                data[chat_id]["game"][i-1] = "🚩"
                        data[chat_id]["game"][choice-1] = "🧨"
                        await query.edit_message_text(f"Minesweeper Game 🪖\n\nYou lost the game. start new game with /start",reply_markup=InlineKeyboardMarkup(make_done_keyboard(data[chat_id]["game"])))
                        await context.bot.setMessageReaction(chat_id=chat_id , message_id=data[chat_id]["message id"], reaction="🔥", is_big=True)
                        time.sleep(1)
                        await context.bot.send_message(text="💣" ,chat_id=chat_id)
                        await query.answer("You lost")
                    else: 
                        pre_opened = copy.deepcopy(data[chat_id]["opened"])
                        data[chat_id]["opened"].append(choice)
                        cycle_opened = []
                        while pre_opened != data[chat_id]["opened"] and cycle_opened != data[chat_id]["opened"]:
                            cycle_opened = copy.deepcopy(data[chat_id]["opened"])
                            for i in list(set(cycle_opened) - set(data[chat_id]["checked"])):
                                if data[chat_id]["table"][i-1] == 0:
                                    if i not in no_after and i not in no_before:
                                        if  data[chat_id]["table"][i-2] != "*" and i - 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-1)
                                        if data[chat_id]["table"][i] != "*" and i + 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+1)
                                        for a in [7,8,9]:
                                            if i-1-a > 0 and data[chat_id]["table"][i-1-a] != "*" and i - a not in data[chat_id]["opened"]:
                                                data[chat_id]["opened"].append(i-a)
                                            if i-1+a < 64 and data[chat_id]["table"][i-1+a] != "*" and i + a not in data[chat_id]["opened"]:
                                                data[chat_id]["opened"].append(i+a)
                                    elif i in no_after:
                                        if data[chat_id]["table"][i-2] != "*" and i - 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-1)
                                        if i - 9 > 0 and data[chat_id]["table"][i-9] != "*" and i - 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-8)
                                        if i - 10 > 0 and data[chat_id]["table"][i-10] != "*" and i - 9 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-9)
                                        if i + 7 < 63 and data[chat_id]["table"][i+7] != "*" and i + 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+8)
                                        if i + 6 < 63 and data[chat_id]["table"][i+6] != "*" and i + 7 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+7)
                                    elif i in no_before:
                                        if data[chat_id]["table"][i] != "*" and i + 1 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i+1)
                                        if i - 9 > 0 and data[chat_id]["table"][i-9] != "*" and i - 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-8)
                                        if i - 8 > 0 and data[chat_id]["table"][i-8] != "*" and i - 7 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i-7)
                                        if i + 7 < 63 and data[chat_id]["table"][i+7] != "*" and i + 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+8)
                                        if i + 8 < 63 and data[chat_id]["table"][i+8] != "*" and i + 9 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i+9)
                                if data[chat_id]["table"][i-1] in [1,2,3,4,5,6,7,8]:
                                    if i not in no_after and i not in no_before:
                                        if  data[chat_id]["table"][i-2] == 0 and i - 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-1)
                                        if data[chat_id]["table"][i] == 0 and i + 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+1)
                                        for a in [7,8,9]:
                                            if i-1-a > 0 and data[chat_id]["table"][i-1-a] == 0 and i - a not in data[chat_id]["opened"]:
                                                data[chat_id]["opened"].append(i-a)
                                            if i-1+a < 64 and data[chat_id]["table"][i-1+a] == 0 and i + a not in data[chat_id]["opened"]:
                                                data[chat_id]["opened"].append(i+a)
                                    elif i in no_after:
                                        if data[chat_id]["table"][i-2] == 0 and i - 1 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-1)
                                        if i - 9 > 0 and data[chat_id]["table"][i-9] == 0 and i - 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-8)
                                        if i - 10 > 0 and data[chat_id]["table"][i-10] == 0 and i - 9 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-9)
                                        if i + 7 < 63 and data[chat_id]["table"][i+7] == 0 and i + 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+8)
                                        if i + 6 < 63 and data[chat_id]["table"][i+6] == 0 and i + 7 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+7)
                                    elif i in no_before:
                                        if data[chat_id]["table"][i] == 0 and i + 1 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i+1)
                                        if i - 9 > 0 and data[chat_id]["table"][i-9] == 0 and i - 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i-8)
                                        if i - 8 > 0 and data[chat_id]["table"][i-8] == 0 and i - 7 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i-7)
                                        if i + 7 < 63 and data[chat_id]["table"][i+7] == 0 and i + 8 not in data[chat_id]["opened"]:
                                            data[chat_id]["opened"].append(i+8)
                                        if i + 8 < 63 and data[chat_id]["table"][i+8] == 0 and i + 9 not in data[chat_id]["opened"]: 
                                            data[chat_id]["opened"].append(i+9)                                
                                data[chat_id]["checked"].append(i)
                            continue
                        for i in data[chat_id]["opened"]:
                            data[chat_id]["game"][i-1] = data[chat_id]["table"][i-1]
                        if sorted(data[chat_id]["opened"]) == list(set(all) - set(data[chat_id]["bomb blocks"])):
                            for i in data[chat_id]["bomb blocks"]:
                                data[chat_id]["game"][i-1] = "💣"
                            elapsed_time = time.time() - data[chat_id]["time"]
                            await query.edit_message_text(f"Minesweeper Game 🪖\n\nCongratulation!! You won the game 🥳\nElapsed time: {elapsed_time:.2f}s",reply_markup=InlineKeyboardMarkup(make_done_keyboard(data[chat_id]["game"])))
                            await context.bot.setMessageReaction(chat_id=chat_id , message_id=data[chat_id]["message id"], reaction="🎉", is_big=True)
                            time.sleep(1)
                            await context.bot.send_message(text="🎉" ,chat_id=chat_id)
                            await query.answer("Game won")
                        else:
                            counter = counting(data[chat_id]["flags"])
                            await query.edit_message_text(f"Minesweeper Game 🪖\n\nMines left: {counter}\nCurrent state: Mine mode 💣", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(data[chat_id]["game"])))
                            await query.answer("New cell opened")
    else:
        await query.answer("Start again", show_alert=True)

def main() -> None:
    application = Application.builder().token('TOKEN @BotFather').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()