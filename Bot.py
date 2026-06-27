```python
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import games  # ← notre fichier games.py

============ CONFIG ============
TOKEN = "8772878613:AAEnlv3sAM6lfwB4hB0iFD1ht6EOKT6oT3M"
ADMIN_ID = 8652730606  # ton ID Telegram
CURRENCY = games.CURRENCY

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(name)

============ MENUS ============
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎰 Slots", callback_data="slots"),
         InlineKeyboardButton("🎡 Roulette", callback_data="roulette")],
        [InlineKeyboardButton("🎲 Dice", callback_data="dice"),
         InlineKeyboardButton("🪙 Pile ou Face", callback_data="coinflip")],
        [InlineKeyboardButton("👤 Profil", callback_data="profile"),
         InlineKeyboardButton("💰 Cashback", callback_data="cashback")],
    ]
    return InlineKeyboardMarkup(keyboard)

def bet_menu(game):
    amounts = [1, 5, 10, 25, 50, 100]
    row = []
    buttons = []
    for a in amounts:
        buttons.append(InlineKeyboardButton(f"{a}{CURRENCY}", callback_data=f"bet_{game}_{a}"))
2 lignes
    return InlineKeyboardMarkup([
        buttons[:3],
        buttons[3:],
        [InlineKeyboardButton("🔙 Retour", callback_data="menu")]
    ])

============ COMMANDES ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    games.get_balance(user.id)  # init
    await update.message.reply_text(
        f"🎰 GameCash — Bienvenue {user.first_name} !\n\n"
        f"💰 Ton solde : {games.get_balance(user.id):.2f}{CURRENCY}\n\n"
        f"Choisis un jeu :",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    await query.edit_message_text(
        f"🎰 GameCash\n💰 Solde : {games.get_balance(user.id):.2f}{CURRENCY}\n\nChoisis un jeu :",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    username = user.username or user.first_name
    profile_text = games.get_profile(user.id, username)
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu")]]
    await query.edit_message_text(profile_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def cashback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    cb = games.apply_cashback(user.id)
    bal = games.get_balance(user.id)
    if cb:
        text = f"💰 Cashback reçu !\n+{cb:.2f}{CURRENCY}\n💰 Nouveau solde : {bal:.2f}{CURRENCY}"
    else:
        text = f"😔 Pas de cashback disponible.\n💰 Solde : {bal:.2f}{CURRENCY}"
    keyboard = [[InlineKeyboardButton("🔙 Retour", callback_data="menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")result, win = games.play_dice(user.id, amount, prediction)
    keyboard = [[InlineKeyboardButton("🔁 Rejouer", callback_data="dice"),
                 InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    await query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def handle_coin_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")  # coin_pile / coin_face
    side = data[1]
    user = query.from_user
    amount = context.user_data.get("bet_amount", 10)
    result, win = games.play_coinflip(user.id, amount, side)
    keyboard = [[InlineKeyboardButton("🔁 Rejouer", callback_data="coinflip"),
                 InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
    await query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

async def handle_roulette_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")  # rcolor_red
    color = data[1]
    keyboard = bet_menu("roulette")
    await query.edit_message_text(f"🎡 Roulette — {color}\nCombien tu mises ?", reply_markup=keyboard, parse_mode="HTML")
    context.user_data["roulette_type"] = "color"
    context.user_data["roulette_value"] = color

============ ADMIN ============
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Tu n'es pas admin.")
        return
    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
        games.add_balance(user_id, amount)
        await update.message.reply_text(f"✅ {amount:.2f}{CURRENCY} ajouté à {user_id}")
    except:
        await update.message.reply_text("Usage: /add <user_id> <amount>")

============ CALLBACK ROUTER ============
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    handlers = {
        "menu": menu,
        "profile": profile,
        "cashback": cashback,
        "slots": play_slots,
        "roulette": play_roulette,
        "dice": play_dice,
        "coinflip": play_coinflip,
    }

    if data in handlers:
        await handlers[data](update, context)
    elif data.startswith("bet_"):
        await handle_bet(update, context)
    elif data.startswith("dice_"):
        await handle_dice_choice(update, context)
    elif data.startswith("coin_"):
        await handle_coin_choice(update, context)
    elif data.startswith("rcolor_"):
        await handle_roulette_color(update, context)

============ MAIN ============
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_balance))
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("🎰 GameCash bot is running...")
    app.run_polling()

if name == "main":
    main()
```

 
