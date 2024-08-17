import random
import copy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

description = "**Minesweeper: Overview and How to Play**\n\n**Objective:**  \nThe goal of Minesweeper is to clear a grid of hidden mines without detonating any. The numbers revealed on the grid indicate how many mines are adjacent to that square, helping you deduce where the mines are hidden.\n\n**How to Play:**\n1. **Start by Clicking a Square:**  \n   - The first click will reveal a number or an empty space. An empty space indicates no adjacent mines.\n\n2. **Understand the Numbers:**  \n   - Each number on a revealed square shows how many mines are adjacent to it (including diagonals). Use this information to figure out where the mines might be.\n\n3. **Clear the Grid:**\n   - If you click on a mine, the game is over.\n   - The game is won when all non-mine squares are revealed.\n\n**Tips:**\n- Start with corners or edges to get better information.\n- If you're unsure, guess, but be cautious!\n\nEnjoy the challenge and improve your strategy with practice!"
no_after = [9,18,27,36,45,54,63,72,81]
no_before = [1,10,19,28,37,46,55,64,73]
game = ["➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖","➖"]
flags = []
opened = []
bomb = True
flag = False

def  make_keyboard(apart):
    keyboard = [
    [InlineKeyboardButton(apart[0][0], callback_data='1'),InlineKeyboardButton(apart[0][1], callback_data='2'), InlineKeyboardButton(apart[0][2], callback_data='3'), InlineKeyboardButton(apart[0][3], callback_data='4'), InlineKeyboardButton(apart[0][4], callback_data='5'), InlineKeyboardButton(apart[0][5], callback_data='6'), InlineKeyboardButton(apart[0][6], callback_data='7'), InlineKeyboardButton(apart[0][7], callback_data='8'), InlineKeyboardButton(apart[0][8], callback_data='9')],
    [InlineKeyboardButton(apart[1][0], callback_data='10'),InlineKeyboardButton(apart[1][1], callback_data='11'), InlineKeyboardButton(apart[1][2], callback_data='12'), InlineKeyboardButton(apart[1][3], callback_data='13'), InlineKeyboardButton(apart[1][4], callback_data='14'), InlineKeyboardButton(apart[1][5], callback_data='15'), InlineKeyboardButton(apart[1][6], callback_data='16'), InlineKeyboardButton(apart[1][7], callback_data='17'), InlineKeyboardButton(apart[1][8], callback_data='18')],
    [InlineKeyboardButton(apart[2][0], callback_data='19'),InlineKeyboardButton(apart[2][1], callback_data='20'), InlineKeyboardButton(apart[2][2], callback_data='21'), InlineKeyboardButton(apart[2][3], callback_data='22'), InlineKeyboardButton(apart[2][4], callback_data='23'), InlineKeyboardButton(apart[2][5], callback_data='24'), InlineKeyboardButton(apart[2][6], callback_data='25'), InlineKeyboardButton(apart[2][7], callback_data='26'), InlineKeyboardButton(apart[2][8], callback_data='27')],
    [InlineKeyboardButton(apart[3][0], callback_data='28'),InlineKeyboardButton(apart[3][1], callback_data='29'), InlineKeyboardButton(apart[3][2], callback_data='30'), InlineKeyboardButton(apart[3][3], callback_data='31'), InlineKeyboardButton(apart[3][4], callback_data='32'), InlineKeyboardButton(apart[3][5], callback_data='33'), InlineKeyboardButton(apart[3][6], callback_data='34'), InlineKeyboardButton(apart[3][7], callback_data='35'), InlineKeyboardButton(apart[3][8], callback_data='36')],
    [InlineKeyboardButton(apart[4][0], callback_data='37'),InlineKeyboardButton(apart[4][1], callback_data='38'), InlineKeyboardButton(apart[4][2], callback_data='39'), InlineKeyboardButton(apart[4][3], callback_data='40'), InlineKeyboardButton(apart[4][4], callback_data='41'), InlineKeyboardButton(apart[4][5], callback_data='42'), InlineKeyboardButton(apart[4][6], callback_data='43'), InlineKeyboardButton(apart[4][7], callback_data='44'), InlineKeyboardButton(apart[4][8], callback_data='45')],
    [InlineKeyboardButton(apart[5][0], callback_data='46'),InlineKeyboardButton(apart[5][1], callback_data='47'), InlineKeyboardButton(apart[5][2], callback_data='48'), InlineKeyboardButton(apart[5][3], callback_data='49'), InlineKeyboardButton(apart[5][4], callback_data='50'), InlineKeyboardButton(apart[5][5], callback_data='51'), InlineKeyboardButton(apart[5][6], callback_data='52'), InlineKeyboardButton(apart[5][7], callback_data='53'), InlineKeyboardButton(apart[5][8], callback_data='54')],
    [InlineKeyboardButton(apart[6][0], callback_data='55'),InlineKeyboardButton(apart[6][1], callback_data='56'), InlineKeyboardButton(apart[6][2], callback_data='57'), InlineKeyboardButton(apart[6][3], callback_data='58'), InlineKeyboardButton(apart[6][4], callback_data='59'), InlineKeyboardButton(apart[6][5], callback_data='60'), InlineKeyboardButton(apart[6][6], callback_data='61'), InlineKeyboardButton(apart[6][7], callback_data='62'), InlineKeyboardButton(apart[6][8], callback_data='63')],
    [InlineKeyboardButton(apart[7][0], callback_data='64'),InlineKeyboardButton(apart[7][1], callback_data='65'), InlineKeyboardButton(apart[7][2], callback_data='66'), InlineKeyboardButton(apart[7][3], callback_data='67'), InlineKeyboardButton(apart[7][4], callback_data='68'), InlineKeyboardButton(apart[7][5], callback_data='69'), InlineKeyboardButton(apart[7][6], callback_data='70'), InlineKeyboardButton(apart[7][7], callback_data='71'), InlineKeyboardButton(apart[7][8], callback_data='72')],
    [InlineKeyboardButton(apart[8][0], callback_data='73'),InlineKeyboardButton(apart[8][1], callback_data='74'), InlineKeyboardButton(apart[8][2], callback_data='75'), InlineKeyboardButton(apart[8][3], callback_data='76'), InlineKeyboardButton(apart[8][4], callback_data='77'), InlineKeyboardButton(apart[8][5], callback_data='78'), InlineKeyboardButton(apart[8][6], callback_data='79'), InlineKeyboardButton(apart[8][7], callback_data='80'), InlineKeyboardButton(apart[8][8], callback_data='81')],
    [InlineKeyboardButton("💣", callback_data='bomb'),InlineKeyboardButton("🚩", callback_data='flag')]
    ]
    return(keyboard)

def chunk(table):
    rows = []
    i = 1
    for n in no_after:
        row = table[n - 9:n]
        rows.append(row)
        i += 1
    return(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bomb_blocks, table
    bomb_blocks = random.sample(range(1, 82), 10)

    table = []
    i = 1
    while i < 82:
        if i in bomb_blocks:
            table.append("*")
        else:
            b = 0
            if i not in no_after and i not in no_before:
                if i + 1 in bomb_blocks:
                    b += 1            
                if i - 1 in bomb_blocks:
                    b += 1
                for num in [8,9,10]:
                    if i - num > 0 :
                        if i - num in bomb_blocks:
                            b += 1
                    if i + num < 82 :
                        if i + num in bomb_blocks:
                            b += 1
            elif i in no_after:
                if i - 1 in bomb_blocks:
                    b += 1            
                if i - 9 > 0 :
                    if i - 9 in bomb_blocks:
                        b += 1
                if i + 9 < 82 :
                    if i + 9 in bomb_blocks:
                        b += 1            
                if i - 10 > 0 :
                    if i - 10 in bomb_blocks:
                        b += 1
                if i + 8 < 82 :
                    if i + 8 in bomb_blocks:
                        b += 1
            elif i in no_before:
                if i + 1 in bomb_blocks:
                    b += 1            
                if i - 9 > 0 :
                    if i - 9 in bomb_blocks:
                        b += 1
                if i + 9 < 82 :
                    if i + 9 in bomb_blocks:
                        b += 1            
                if i - 8 > 0 :
                    if i - 8 in bomb_blocks:
                        b += 1
                if i + 10 < 82 :
                    if i + 10 in bomb_blocks:
                        b += 1
            table.append(b)
        i += 1
        continue
    
    await update.message.reply_text(description, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global flag, bomb, bomb_blocks, table
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == "flag":
        flag = True
        bomb = False
        await query.edit_message_text(f"{description}\n\n⭕**Alert : Falg mode enabled**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
    elif choice == "bomb":
        flag = False
        bomb = True
        await query.edit_message_text(f"{description}\n\n⭕**Alert : Bomb mode enabled**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
    else: 
        choice = int(choice)
        if flag:
            if choice not in flags :
                game[choice - 1] = "🚩"
                flags.append(choice)
                await query.edit_message_text(f"{description}\n\n⭕**Alert : Flag added**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
            else:
                game[choice - 1] = "➖"
                flags.remove(choice)
                await query.edit_message_text(f"{description}\n\n⭕**Alert : Flag removed**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
        elif bomb:
            if choice in flags:
                await query.edit_message_text(f"{description}\n\n⭕**Alert : It's Flag! you have to remove it fisrt**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))
            else: 
                if choice in bomb_blocks:
                    await query.edit_message_text("You lost",reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game)))) # make function for a lost game with different call backs
                else: 
                    pre_opened = copy.deepcopy(opened)
                    opened.append(choice)
                    cycle_opened = []
                    while pre_opened != opened and cycle_opened != opened:
                        cycle_opened = copy.deepcopy(opened)
                        for i in opened:
                            if i == 0:
                                if i not in no_after and i not in no_before:
                                    if  table[i-2] != "*":
                                        opened.append(i-1)
                                    if table[i] != "*":
                                        opened.append(i+1)
                                    for a in [7,8,9]:
                                        if table[i-1-a] != "*" and i-1-a > 0:
                                            opened.append(i-a)
                                        if table[i-1+a] != "*" and i-1+a < 81:
                                            opened.append(i+a)
                                elif i in no_after:
                                    if table[i-2] != "*":
                                        opened.append(i-1)
                                    if table[i-10] != "*" and i - 10 > 0:
                                        opened.append(i-9)
                                    if table[i-11] != "*" and i - 11 > 0:
                                        opened.append(i-10)
                                    if table[i+8] != "*" and i + 8 < 80:
                                        opened.append(i+9)
                                    if table[i+7] != "*" and i + 7 < 80:
                                        opened.append(i+8)
                                elif i in no_before:
                                    if table[i] != "*": 
                                        opened.append(i+1)
                                    if table[i-10] != "*" and i - 10 > 0:
                                        opened.append(i-9)
                                    if table[i-9] != "*" and i - 9 > 0: 
                                        opened.append(i-8)
                                    if table[i+8] != "*" and i + 8 < 80:
                                        opened.append(i+9)
                                    if table[i+9] != "*" and i + 9 < 80: 
                                        opened.append(i+10)
                        continue
                    for i in opened:
                        game[i-1] = table[i-1]
                    await query.edit_message_text(f"{description}\n\n⭕**Alert : New cell opened**", parse_mode='Markdown',reply_markup=InlineKeyboardMarkup(make_keyboard(chunk(game))))

def main() -> None:
    application = Application.builder().token('7538249939:AAEeQzgiD-42si5VkG0DQipTm7IwYo9unpk').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()