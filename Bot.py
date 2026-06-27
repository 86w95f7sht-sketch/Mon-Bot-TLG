```python
import os
import logging
import random
from decimal import Decimal
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

═══════════════════════════════════════
CONFIG
═══════════════════════════════════════
TOKEN = os.getenv("BOT_TOKEN", "TON_TOKEN_ICI")
CURRENCY = "💎"
ADMIN_ID = 8652730606

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(name)

═══════════════════════════════════════
BASE DE DONNÉES (fichier JSON simple)
═══════════════════════════════════════
import json

DB_FILE = "gamecash_db.json"

def _load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def _save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def get_balance(user_id):
    db = _load_db()
    uid = str(user_id)
    return float(db.get(uid, {}).get("balance", 100))

def add_balance(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 100, "deposited": 0}
    db[uid]["balance"] = float(db[uid]["balance"]) + amount
    _save_db(db)

def get_total_deposited(user_id):
    db = _load_db()
    uid = str(user_id)
    return float(db[uid].get("deposited", 0)) if uid in db else 0

def add_deposit(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 100, "deposited": 0}
    db[uid]["balance"] = float(db[uid]["balance"]) + amount
    db[uid]["deposited"] = float(db[uid]["deposited"]) + amount
    _save_db(db)

═══════════════════════════════════════
IMPORTS DES JEUX
═══════════════════════════════════════
from games import jouer_slots, jouer_dice, jouer_baccarat

═══════════════════════════════════════
MENUS
═══════════════════════════════════════
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎰 Slots", callback_data="slots"),
         InlineKeyboardButton("🎲 Dice", callback_data="dice")],
        [InlineKeyboardButton("🃏 Baccarat", callback_data="baccarat"),
         InlineKeyboardButton("🪙 Pile ou Face", callback_data="coinflip")],
        [InlineKeyboardButton("🔴⚫ Roulette", callback_data="roulette"),
         InlineKeyboardButton("💰 Solde", callback_data="balance")],
        [InlineKeyboardButton("💳 Déposer", callback_data="deposit"),
         InlineKeyboardButton("👤 Profil", callback_data="profil")],
    ]
    return InlineKeyboardMarkup(keyboard)

def bet_menu(game):
    amounts = [1, 5, 10, 25, 50, 100]
    keyboard = []
    row = []
    for i, a in enumerate(amounts):
        row.append(InlineKeyboardButton(f"{a}{CURRENCY}", callback_data=f"bet_{game}_{a}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Retour", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

═══════════════════════════════════════
HANDLERS
═══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_userbal = get_balance(user.id)

Premier lancement
    db = _load_db()
    if str(user.id) not in db:
        db[str(user.id)] = {"balance": 100, "deposited": 0}
        _save_db(db)

    await update.message.reply_text(
        f"🎰 GameCash — Bienvenue {user.first_name} !\n\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n\n"
        f"Choisis un jeu dans le menu 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    bal = get_balance(user.id)
    dep = get_total_deposited(user.id)
    await q.edit_message_text(
        f"👤 {user.first_name}\n\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n"
        f"💳 Total déposé : {dep:.2f}{CURRENCY}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown",
    )

async def profil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    bal = get_balance(user.id)
    dep = get_total_deposited(user.id)

    msg = (
        f"👤 Profil GameCash\n\n"
        f"🆔 ID : {user.id}\n"
        f"📛 Nom : {user.first_name}\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n"
        f"💳 Total déposé : {dep:.2f}{CURRENCY}\n"
    )
    await q.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown",
    )

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "💳 Déposer des fonds\n\n"
        "Contacte l'admin pour déposer : @jesaispas34\n\n"
        "Ou utilise la commande :\n"
        "/add MONTANT",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
        ]),
        parse_mode="Markdown",
    )

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Seul l'admin peut ajouter des fonds.")
        return

    try:
        amount = float(context.args[0])
        if amount <= 0:
            raise ValueError
Par défaut ajoute à l'expéditeur, sinon au cible
        target_id = user.id
        if len(context.args) > 1:
            target_id = int(context.args[1].replace("@", ""))
        add_deposit(target_id, amount)
        bal = get_balance(target_id)
        await update.message.reply_text(
            f"✅ {amount}{CURRENCY} ajouté à {target_id}\n"
            f"💰 Nouveau solde : {bal:.2f}{CURRENCY}",
            parse_mode="HTML",
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Usage : /add MONTANT [USER_ID]")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    bal = get_balance(user.id)
    await q.edit_message_text(
        f"🎰 GameCash — {user.first_name}\n💰 {bal:.2f}{CURRENCY}",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

═══════════════════════════════════════
GAME HANDLERS
═══════════════════════════════════════
async def play_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🎰 Mise ?", reply_markup=bet_menu("slots"))
    context.user_data["game"] = "slots"

async def play_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🎲 Mise ?", reply_markup=bet_menu("dice"))
    context.user_data["game"] = "dice"

async def play_baccarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🃏 Mise ?", reply_markup=bet_menu("baccarat"))
    context.user_data["game"] = "baccarat"

async def play_coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🪙 Mise ?", reply_markup=bet_menu("coinflip"))
    context.user_data["game"] = "coinflip"

async def play_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🔴⚫ Mise ?", reply_markup=bet_menu("roulette"))
    context.user_data["game"] = "roulette"

═══════════════════════════════════════
BET HANDLER (résultat des jeux)
═══════════════════════════════════════
async def handle_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data.split("_")
    game = data[1]
    amount = float(data[2])
    user = q.from_user

    result_text = ""
    if game == "slots":
        result_text, _ = jouer_slots(user.id, amount)
    elif game == "dice":
        result_text, _ = jouer_dice(user.id, amount)
    elif game == "baccarat":
        from games import jouer_baccarat
        result_text, _ = jouer_baccarat(user.id, amount)
    elif game == "coinflip":
        from games import jouer_coinflip
        result_text, _ = jouer_coinflip(user.id, amount)
    elif game == "roulette":
        from games import jouer_roulette
        result_text, _ = jouer_roulette(user.id, amount)
    else:
        result_text = "❌ Jeu inconnu"

    kb = [
        [InlineKeyboardButton("🔁 Rejouer", callback_data=game),
         InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ]
    await q.edit_message_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )

═══════════════════════════════════════
CALLBACK ROUTER
═══════════════════════════════════════
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    handlers = {
        "menu": menu,
        "balance": balance,
        "deposit": deposit,
        "profil": profil,
        "slots": play_slots,
        "dice": play_dice,
        "baccarat": play_baccarat,
        "coinflip": play_coinflip,
        "roulette": play_roulette,
    }

    if data in handlers:
        await handlers[data](update, context)
    elif data.startswith("bet_"):
        await handle_bet(update, context)

═══════════════════════════════════════
MAIN
═══════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CallbackQueryHandler(callback_handler))logger.info("🎰 GameCash bot démarré !")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if name == "main":
    main()
