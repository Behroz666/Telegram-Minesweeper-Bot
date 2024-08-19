import random
import copy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

#TODO add game over and won view
#TODO add more cosmetic stuff and rewrite the tutorial (send it seprately)
#TODO add reaction/emoji for lose or win
#TODO make sure that first oppend cell is not bomb
#TODO add a check list for cells to make  loops more efficient
#TODO add json handling for multiple users

description = "**Minesweeper: Overview and How to Play**\n\n**Objective:**  \nThe goal of Minesweeper is to clear a grid of hidden mines without detonating any. The numbers revealed on the grid indicate how many mines are adjacent to that square, helping you deduce where the mines are hidden.\n\n**How to Play:**\n1. **Start by Clicking a Square:**  \n   - The first click will reveal a number or an empty space. An empty space indicates no adjacent mines.\n\n2. **Understand the Numbers:**  \n   - Each number on a revealed square shows how many mines are adjacent to it (including diagonals). Use this information to figure out where the mines might be.\n\n3. **Clear the Grid:**\n   - If you click on a mine, the game is over.\n   - The game is won when all non-mine squares are revealed.\n\n**Tips:**\n- Start with corners or edges to get better information.\n- If you're unsure, guess, but be cautious!\n\nEnjoy the challenge and improve your strategy with practice!"
all = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]
no_after = [8,16,24,32,40,48,56,64]
no_before = [1,9,17,25,33,41,49,57]
flags = []
opened = []
bomb = True
flag = False

def  make_keyboard(apart):
    keyboard = [
    [InlineKeyboardButton(apart[0][0], callback_data='1'),InlineKeyboardButton(apart[0][1], callback_data='2'), InlineKeyboardButton(apart[0][2], callback_data='3'), InlineKeyboardButton(apart[0][3], callback_data='4'), InlineKeyboardButton(apart[0][4], callback_data='5'), InlineKeyboardButton(apart[0][5], callback_data='6'), InlineKeyboardButton(apart[0][6], callback_data='7'), InlineKeyboardButton(apart[0][7], callback_data='8')],
    [InlineKeyboardButton(apart[1][0], callback_data='9'),InlineKeyboardButton(apart[1][1], callback_data='10'), InlineKeyboardButton(apart[1][2], callback_data='11'), InlineKeyboardButton(apart[1][3], callback_data='12'), InlineKeyboardButton(apart[1][4], callback_data='13'), InlineKeyboardButton(apart[1][5], callback_data='14'), InlineKeyboardButton(apart[1][6], callback_data='15'), InlineKeyboardButton(apart[1][7], callback_data='16')],
    [InlineKeyboardButton(apart[2][0], callback_data='17'),InlineKeyboardButton(apart[2][1], callback_data='18'), InlineKeyboardButton(apart[2][2], callback_data='19'), InlineKeyboardButton(apart[2][3], callback_data='20'), InlineKeyboardButton(apart[2][4], callback_data='21'), InlineKeyboardButton(apart[2][5], callback_data='22'), InlineKeyboardButton(apart[2][6], callback_data='23'), InlineKeyboardButton(apart[2][7], callback_data='24')],
    [InlineKeyboardButton(apart[3][0], callback_data='25'),InlineKeyboardButton(apart[3][1], callback_data='26'), InlineKeyboardButton(apart[3][2], callback_data='27'), InlineKeyboardButton(apart[3][3], callback_data='28'), InlineKeyboardButton(apart[3][4], callback_data='29'), InlineKeyboardButton(apart[3][5], callback_data='30'), InlineKeyboardButton(apart[3][6], callback_data='31'), InlineKeyboardButton(apart[3][7], callback_data='32')],
    [InlineKeyboardButton(apart[4][0], callback_data='33'),InlineKeyboardButton(apart[4][1], callback_data='34'), InlineKeyboardButton(apart[4][2], callback_data='35'), InlineKeyboardButton(apart[4][3], callback_data='36'), InlineKeyboardButton(apart[4][4], callback_data='37'), InlineKeyboardButton(apart[4][5], callback_data='38'), InlineKeyboardButton(apart[4][6], callback_data='39'), InlineKeyboardButton(apart[4][7], callback_data='40')],
    [InlineKeyboardButton(apart[5][0], callback_data='41'),InlineKeyboardButton(apart[5][1], callback_data='42'), InlineKeyboardButton(apart[5][2], callback_data='43'), InlineKeyboardButton(apart[5][3], callback_data='44'), InlineKeyboardButton(apart[5][4], callback_data='45'), InlineKeyboardButton(apart[5][5], callback_data='46'), InlineKeyboardButton(apart[5][6], callback_data='47'), InlineKeyboardButton(apart[5][7], callback_data='48')],
    [InlineKeyboardButton(apart[6][0], callback_data='49'),InlineKeyboardButton(apart[6][1], callback_data='50'), InlineKeyboardButton(apart[6][2], callback_data='51'), InlineKeyboardButton(apart[6][3], callback_data='52'), InlineKeyboardButton(apart[6][4], callback_data='53'), InlineKeyboardButton(apart[6][5], callback_data='54'), InlineKeyboardButton(apart[6][6], callback_data='55'), InlineKeyboardButton(apart[6][7], callback_data='56')],
    [InlineKeyboardButton(apart[7][0], callback_data='57'),InlineKeyboardButton(apart[7][1], callback_data='58'), InlineKeyboardButton(apart[7][2], callback_data='59'), InlineKeyboardButton(apart[7][3], callback_data='60'), InlineKeyboardButton(apart[7][4], callback_data='61'), InlineKeyboardButton(apart[7][5], callback_data='62'), InlineKeyboardButton(apart[7][6], callback_data='63'), InlineKeyboardButton(apart[7][7], callback_data='64')],
    [InlineKeyboardButton("💣", callback_data='bomb'),InlineKeyboardButton("🚩", callback_data='flag')]
    ]
    return(keyboard)

def  make_done_keyboard(apart):
    keyboard = [
    [InlineKeyboardButton(apart[0][0], callback_data='done'),InlineKeyboardButton(apart[0][1], callback_data='done'), InlineKeyboardButton(apart[0][2], callback_data='done'), InlineKeyboardButton(apart[0][3], callback_data='done'), InlineKeyboardButton(apart[0][4], callback_data='done'), InlineKeyboardButton(apart[0][5], callback_data='done'), InlineKeyboardButton(apart[0][6], callback_data='done'), InlineKeyboardButton(apart[0][7], callback_data='done')],
    [InlineKeyboardButton(apart[1][0], callback_data='done'),InlineKeyboardButton(apart[1][1], callback_data='done'), InlineKeyboardButton(apart[1][2], callback_data='done'), InlineKeyboardButton(apart[1][3], callback_data='done'), InlineKeyboardButton(apart[1][4], callback_data='done'), InlineKeyboardButton(apart[1][5], callback_data='done'), InlineKeyboardButton(apart[1][6], callback_data='done'), InlineKeyboardButton(apart[1][7], callback_data='done')],
    [InlineKeyboardButton(apart[2][0], callback_data='done'),InlineKeyboardButton(apart[2][1], callback_data='done'), InlineKeyboardButton(apart[2][2], callback_data='done'), InlineKeyboardButton(apart[2][3], callback_data='done'), InlineKeyboardButton(apart[2][4], callback_data='done'), InlineKeyboardButton(apart[2][5], callback_data='done'), InlineKeyboardButton(apart[2][6], callback_data='done'), InlineKeyboardButton(apart[2][7], callback_data='done')],
    [InlineKeyboardButton(apart[3][0], callback_data='done'),InlineKeyboardButton(apart[3][1], callback_data='done'), InlineKeyboardButton(apart[3][2], callback_data='done'), InlineKeyboardButton(apart[3][3], callback_data='done'), InlineKeyboardButton(apart[3][4], callback_data='done'), InlineKeyboardButton(apart[3][5], callback_data='done'), InlineKeyboardButton(apart[3][6], callback_data='done'), InlineKeyboardButton(apart[3][7], callback_data='done')],
    [InlineKeyboardButton(apart[4][0], callback_data='done'),InlineKeyboardButton(apart[4][1], callback_data='done'), InlineKeyboardButton(apart[4][2], callback_data='done'), InlineKeyboardButton(apart[4][3], callback_data='done'), InlineKeyboardButton(apart[4][4], callback_data='done'), InlineKeyboardButton(apart[4][5], callback_data='done'), InlineKeyboardButton(apart[4][6], callback_data='done'), InlineKeyboardButton(apart[4][7], callback_data='done')],
    [InlineKeyboardButton(apart[5][0], callback_data='done'),InlineKeyboardButton(apart[5][1], callback_data='done'), InlineKeyboardButton(apart[5][2], callback_data='done'), InlineKeyboardButton(apart[5][3], callback_data='done'), InlineKeyboardButton(apart[5][4], callback_data='done'), InlineKeyboardButton(apart[5][5], callback_data='done'), InlineKeyboardButton(apart[5][6], callback_data='done'), InlineKeyboardButton(apart[5][7], callback_data='done')],
    [InlineKeyboardButton(apart[6][0], callback_data='done'),InlineKeyboardButton(apart[6][1], callback_data='done'), InlineKeyboardButton(apart[6][2], callback_data='done'), InlineKeyboardButton(apart[6][3], callback_data='done'), InlineKeyboardButton(apart[6][4], callback_data='done'), InlineKeyboardButton(apart[6][5], callback_data='done'), InlineKeyboardButton(apart[6][6], callback_data='done'), InlineKeyboardButton(apart[6][7], callback_data='done')],
    [InlineKeyboardButton(apart[7][0], callback_data='done'),InlineKeyboardButton(apart[7][1], callback_data='done'), InlineKeyboardButton(apart[7][2], callback_data='done'), InlineKeyboardButton(apart[7][3], callback_data='done'), InlineKeyboardButton(apart[7][4], callback_data='done'), InlineKeyboardButton(apart[7][5], callback_data='done'), InlineKeyboardButton(apart[7][6], callback_data='done'), InlineKeyboardButton(apart[7][7], callback_data='done')],
    ]
    return(keyboard)

def chunk(table):
    rows = []
    i = 1
    for n in no_after:
        row = table[n - 8:n]
        rows.append(row)
        i += 1
    return(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bomb_blocks, table, game, opened
    game = ["➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖"]
    bomb_blocks = sorted(random.sample(range(1, 65), 10))
    table = []
    opened=[]
    i = 1
    while i < 65:
        if i in bomb_blocks:
            table.append("*")
        else:
            b = 0
            if i not in no_after and i not in no_before:
                if i + 1 in bomb_blocks:
                    b += 1            
                if i - 1 in bomb_blocks:
                    b += 1
                for num in [7,8,9]:
                    if i - num > 0 :
                        if i - num in bomb_blocks:
                            b += 1
                    if i + num < 65 :
                        if i + num in bomb_blocks:
                            b += 1
            elif i in no_after:
                if i - 1 in bomb_blocks:
                    b += 1            
                if i - 8 > 0 :
                    if i - 8 in bomb_blocks:
                        b += 1
                if i + 8 < 65 :
                    if i + 8 in bomb_blocks:
                        b += 1            
                if i - 9 > 0 :
                    if i - 9 in bomb_blocks:
                        b += 1
                if i + 7 < 65 :
                    if i + 7 in bomb_blocks:
                        b += 1
            elif i in no_before:
                if i + 1 in bomb_blocks:
                    b += 1            
                if i - 8 > 0 :
                    if i - 8 in bomb_blocks:
                        b += 1
                if i + 8 < 65 :
                    if i + 8 in bomb_blocks:
                        b += 1            
                if i - 7 > 0 :
                    if i - 7 in bomb_blocks:
                        b += 1
                if i + 9 < 65 :
                    if i + 9 in bomb_blocks:
                        b += 1
            table.append(b)
        i += 1
        continue
    print(bomb_blocks)
    for qqq in chunk(table):
        print(qqq)
    await update.message.reply_text(description, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flag, bomb, bomb_blocks, table, no_after, no_before, game, all
    query = update.callback_query
    #await query.answer()
    choice = query.data
    if choice == "flag":
        flag = True
        bomb = False
        await query.answer("Flag mode enabled")
    elif choice == "bomb":
        flag = False
        bomb = True
        await query.answer("Bomb mode enabled")
    elif choice == "done":
        await query.answer("Your game is done. use /start")
    else: 
        choice = int(choice)
        if flag:
            if choice not in flags :
                game[choice - 1] = "🚩"
                flags.append(choice)
                await query.edit_message_text(description, parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
                await query.answer("Flag added")
            else:
                game[choice - 1] = "➖"
                flags.remove(choice)
                await query.edit_message_text(description, parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
                await query.answer("Flag removed")
        elif bomb:
            if choice in flags:
                await query.answer("It's Flag! you have to remove it fisrt")
            elif choice in opened:
                await query.answer("Cell already openned")
            else: 
                if choice in bomb_blocks:
                    for i in bomb_blocks:
                        game[i-1] = "💣"
                    game[choice-1] = "🧨"
                    await query.edit_message_text("You lost",reply_markup=InlineKeyboardMarkup(make_done_keyboard(chunk(game))))
                else: 
                    pre_opened = copy.deepcopy(opened)
                    opened.append(choice)
                    cycle_opened = []
                    while pre_opened != opened and cycle_opened != opened:
                        cycle_opened = copy.deepcopy(opened)
                        for i in cycle_opened:
                            if table[i-1] == 0:
                                if i not in no_after and i not in no_before:
                                    if  table[i-2] != "*" and i - 1 not in opened:
                                        opened.append(i-1)
                                    if table[i] != "*" and i + 1 not in opened:
                                        opened.append(i+1)
                                    for a in [7,8,9]:
                                        if i-1-a > 0 and table[i-1-a] != "*" and i - a not in opened:
                                            opened.append(i-a)
                                        if i-1+a < 64 and table[i-1+a] != "*" and i + a not in opened:
                                            opened.append(i+a)
                                elif i in no_after:
                                    if table[i-2] != "*" and i - 1 not in opened:
                                        opened.append(i-1)
                                    if i - 9 > 0 and table[i-9] != "*" and i - 8 not in opened:
                                        opened.append(i-8)
                                    if i - 10 > 0 and table[i-10] != "*" and i - 9 not in opened:
                                        opened.append(i-9)
                                    if i + 7 < 63 and table[i+7] != "*" and i + 8 not in opened:
                                        opened.append(i+8)
                                    if i + 6 < 63 and table[i+6] != "*" and i + 7 not in opened:
                                        opened.append(i+7)
                                elif i in no_before:
                                    if table[i] != "*" and i + 1 not in opened: 
                                        opened.append(i+1)
                                    if i - 9 > 0 and table[i-9] != "*" and i - 8 not in opened:
                                        opened.append(i-8)
                                    if i - 8 > 0 and table[i-8] != "*" and i - 7 not in opened: 
                                        opened.append(i-7)
                                    if i + 7 < 63 and table[i+7] != "*" and i + 8 not in opened:
                                        opened.append(i+8)
                                    if i + 8 < 63 and table[i+8] != "*" and i + 9 not in opened: 
                                        opened.append(i+9)
                            if table[i-1] in [1,2,3,4,5,6,7,8]:
                                if i not in no_after and i not in no_before:
                                    if  table[i-2] == 0 and i - 1 not in opened:
                                        opened.append(i-1)
                                    if table[i] == 0 and i + 1 not in opened:
                                        opened.append(i+1)
                                    for a in [7,8,9]:
                                        if i-1-a > 0 and table[i-1-a] == 0 and i - a not in opened:
                                            opened.append(i-a)
                                        if i-1+a < 64 and table[i-1+a] == 0 and i + a not in opened:
                                            opened.append(i+a)
                                elif i in no_after:
                                    if table[i-2] == 0 and i - 1 not in opened:
                                        opened.append(i-1)
                                    if i - 9 > 0 and table[i-9] == 0 and i - 8 not in opened:
                                        opened.append(i-8)
                                    if i - 10 > 0 and table[i-10] == 0 and i - 9 not in opened:
                                        opened.append(i-9)
                                    if i + 7 < 63 and table[i+7] == 0 and i + 8 not in opened:
                                        opened.append(i+8)
                                    if i + 6 < 63 and table[i+6] == 0 and i + 7 not in opened:
                                        opened.append(i+7)
                                elif i in no_before:
                                    if table[i] == 0 and i + 1 not in opened: 
                                        opened.append(i+1)
                                    if i - 9 > 0 and table[i-9] == 0 and i - 8 not in opened:
                                        opened.append(i-8)
                                    if i - 8 > 0 and table[i-8] == 0 and i - 7 not in opened: 
                                        opened.append(i-7)
                                    if i + 7 < 63 and table[i+7] == 0 and i + 8 not in opened:
                                        opened.append(i+8)
                                    if i + 8 < 63 and table[i+8] == 0 and i + 9 not in opened: 
                                        opened.append(i+9)                                
                        continue
                    for i in opened:
                        game[i-1] = table[i-1]
                    if sorted(opened) == list(set(all) - set(bomb_blocks)):
                        for i in bomb_blocks:
                            game[i-1] = "💣"
                        await query.edit_message_text("You won",reply_markup=InlineKeyboardMarkup(make_done_keyboard(chunk(game))))
                    else:
                        await query.edit_message_text(description, parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
                        await query.answer("New cell opened")

def main() -> None:
    application = Application.builder().token('7538249939:AAEeQzgiD-42si5VkG0DQipTm7IwYo9unpk').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()