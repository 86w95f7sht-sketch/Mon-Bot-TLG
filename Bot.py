```python
import os, logging, random, json
from decimal import Decimal
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

═══════════ CONFIG ═══════════
TOKEN = os.getenv("BOT_TOKEN", "TON_TOKEN_ICI")
CURRENCY = "💎"
ADMIN_ID = 8652730606

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(name)

═══════════ DB ═══════════
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

def set_balance(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 100, "deposited": 0}
    db[uid]["balance"] = float(amount)
    _save_db(db)

def add_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    set_balance(user_id, bal)
    return bal

def get_deposited(user_id):
    db = _load_db()
    uid = str(user_id)
    return float(db.get(uid, {}).get("deposited", 0))

def add_deposit(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 100, "deposited": 0}
    db[uid]["balance"] = float(db[uid]["balance"]) + amount
    db[uid]["deposited"] = float(db[uid]["deposited"]) + amount
    _save_db(db)

═══════════ IMPORTS JEUX ═══════════
from games import jouer_slots, jouer_dice, jouer_baccarat, jouer_coinflip, jouer_roulette

═══════════ MENUS ═══════════
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

═══════════ HANDLERS ═══════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
Créer le compte si pas existantu
    db = _load_db()if str(user.id) not in db:
        db[str(user.id)] = {"balance": 100, "deposited": 0}
        _save_db(db)

    bal = get_balance(user.id)
    await update.message.reply_text(
        f"🎰 GameCash — Bienvenue {user.first_name} !\n\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n\n"
        f"Choisis un jeu dans le menu 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )

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

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    bal = get_balance(user.id)
    dep = get_deposited(user.id)
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
    dep = get_deposited(user.id)
    await q.edit_message_text(
        f"👤 Profil GameCash\n\n"
        f"🆔 ID : {user.id}\n"
        f"📛 Nom : {user.first_name}\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n"
        f"💳 Total déposé : {dep:.2f}{CURRENCY}",
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

═══════════ JEUX ═══════════
async def play_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["game"] = "slots"
    bal = get_balance(q.from_user.id)
    await q.edit_message_text(f"🎰 Slots — Solde : {bal:.2f}{CURRENCY}\n\nChoisis ta mise :",
        reply_markup=bet_menu("slots")
    )

async def play_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["game"] = "dice"
    bal = get_balance(q.from_user.id)
    await q.edit_message_text(
        f"🎲 Dice — Solde : {bal:.2f}{CURRENCY}\n\nChoisis ta mise :",
        reply_markup=bet_menu("dice")
    )

async def play_baccarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["game"] = "baccarat"
    bal = get_balance(q.from_user.id)
    await q.edit_message_text(
        f"🃏 Baccarat — Solde : {bal:.2f}{CURRENCY}\n\nChoisis ta mise :",
        reply_markup=bet_menu("baccarat")
    )

async def play_coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["game"] = "coinflip"
    bal = get_balance(q.from_user.id)
    await q.edit_message_text(
        f"🪙 Pile ou Face — Solde : {bal:.2f}{CURRENCY}\n\nChoisis ta mise :",
        reply_markup=bet_menu("coinflip")
    )

async def play_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["game"] = "roulette"
    bal = get_balance(q.from_user.id)
    await q.edit_message_text(
        f"🔴⚫ Roulette — Solde : {bal:.2f}{CURRENCY}\n\nChoisis ta mise :",
        reply_markup=bet_menu("roulette")
    )

async def handle_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data.split("_")
    game = data[1]
    amount = float(data[2])
    user = q.from_user

    games = {
        "slots": jouer_slots,
        "dice": jouer_dice,
        "baccarat": jouer_baccarat,
        "coinflip": jouer_coinflip,
        "roulette": jouer_roulette,
    }

    result_text, _ = games[game](user.id, amount)
    kb = [
        [InlineKeyboardButton("🔁 Rejouer", callback_data=game),
         InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ]
    await q.edit_message_text(result_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

═══════════ CALLBACK ROUTER ═══════════
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

═══════════ MAIN ═══════════
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
⚠️ AUCUN MessageHandler !!
    logger.info("🎰 GameCash bot démarré !")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if name == "main":
    main()

---

## 📄 `games.py` (à remplacer — version FINALE avec tout)
python
import random, json, os

═══════════ CONFIG ═══════════
START_BALANCE = 0.0
CURRENCY = "💎"DB_FILE = "gamecash_db.json"

═══════════ DB ═══════════
def _load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def get_balance(user_id):
    db = _load_db()
    uid = str(user_id)
    return float(db.get(uid, {}).get("balance", 100))

def set_balance(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 100, "deposited": 0}
    db[uid]["balance"] = float(amount)
    _save_db(db)

def add_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    if bal < 0:
        bal = 0
    set_balance(user_id, bal)
    return bal

═══════════ SLOTS ═══════════
def jouer_slots(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", 0

    add_balance(user_id, -bet)
    icons = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣", "⭐"]
    r = [random.randint(0, 7) for _ in range(3)]
    line = f"| {icons[r[0]]} | {icons[r[1]]} | {icons[r[2]]} |"

    payouts = {
        (0,0,0): 5, (1,1,1): 5, (2,2,2): 5, (3,3,3): 5,
        (4,4,4): 10, (5,5,5): 15, (6,6,6): 50, (7,7,7): 100,
    }
    mult = payouts.get((r[0], r[1], r[2]), 0)
    win = bet * mult if mult > 0 else 0

    if win > 0:
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = f"🎰 Slots\n\n{line}\n\n✅ Gagné ! +{win:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    else:
        bal2 = get_balance(user_id)
        msg = f"🎰 Slots\n\n{line}\n\n❌ Perdu... -{bet:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    return msg, win

═══════════ DICE ═══════════
def jouer_dice(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", 0

    add_balance(user_id, -bet)
    dice = random.randint(1, 6)
    target = random.randint(3, 4)

    if dice >= target:
        win = bet * 1.8
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = f"🎲 Dice\n\n🎲 Résultat : {dice}\n🎯 Cible : {target}+\n\n✅ Gagné ! +{win:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    else:
        bal2 = get_balance(user_id)
        msg = f"🎲 Dice\n\n🎲 Résultat : {dice}\n🎯 Cible : {target}+\n\n❌ Perdu... -{bet:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    return msg, dice >= target

═══════════ BACCARAT ═══════════
def jouer_baccarat(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", 0

    add_balance(user_id, -bet)

Cartes
    def carte():
        return random.choice(["2","3","4","5","6","7","8","9","10","J","Q","K","A"])

    def valeur(cartes):
        t = 0
        for c in cartes:
            if c in ["J","Q","K"]:
                t += 0
            elif c == "A":
                t += 1
            else:
                t += int(c)
        return t % 10

    joueur = [carte(), carte()]
    banque = [carte(), carte()]
    v_joueur = valeur(joueur)
    v_banque = valeur(banque)

    if v_joueur > v_banque:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)msg = f"🃏 Baccarat\n\n🧑 Joueur : {' '.join(joueur)} = {v_joueur}\n🏦 Banque : {' '.join(banque)} = {v_banque}\n\n✅ Joueur gagne ! +{win:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    elif v_banque > v_joueur:
        bal2 = get_balance(user_id)
        msg = f"🃏 Baccarat\n\n🧑 Joueur : {' '.join(joueur)} = {v_joueur}\n🏦 Banque : {' '.join(banque)} = {v_banque}\n\n❌ Banque gagne... -{bet:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    else:
        add_balance(user_id, bet)  # remboursé
        bal2 = get_balance(user_id)
        msg = f"🃏 Baccarat\n\n🧑 Joueur : {' '.join(joueur)} = {v_joueur}\n🏦 Banque : {' '.join(banque)} = {v_banque}\n\n🤝 Égalité ! Remboursé\n💰 Solde : {bal2:.2f}{CURRENCY}"
    return msg, win if v_joueur > v_banque else 0

═══════════ COINFLIP ═══════════
def jouer_coinflip(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", 0

    add_balance(user_id, -bet)
    result = random.choice(["Pile", "Face"])
    choix = random.choice(["Pile", "Face"])

    if result == choix:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = f"🪙 Pile ou Face\n\n🪙 Résultat : {result}\n🎯 Ton choix : {choix}\n\n✅ Gagné ! +{win:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    else:
        bal2 = get_balance(user_id)
        msg = f"🪙 Pile ou Face\n\n🪙 Résultat : {result}\n🎯 Ton choix : {choix}\n\n❌ Perdu... -{bet:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    return msg, result == choix

═══════════ ROULETTE ═══════════
def jouer_roulette(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", 0

    add_balance(user_id, -bet)
    num = random.randint(0, 36)

Couleurs
    if num == 0:
        color = "🟢 Vert"
    elif 1 <= num <= 10:
        color = "🔴 Rouge" if num % 2 == 1 else "⚫ Noir"
    elif 11 <= num <= 18:
        color = "⚫ Noir" if num % 2 == 1 else "🔴 Rouge"
    elif 19 <= num <= 28:
        color = "🔴 Rouge" if num % 2 == 1 else "⚫ Noir"
    else:
        color = "⚫ Noir" if num % 2 == 1 else "🔴 Rouge"

    mise_couleur = random.choice(["🔴 Rouge", "⚫ Noir"])

    if color == mise_couleur:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = f"🔴⚫ Roulette\n\n🎱 Numéro : {num} {color}\n🎯 Mise : {mise_couleur}\n\n✅ Gagné ! +{win:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    else:
        bal2 = get_balance(user_id)
        msg = f"🔴⚫ Roulette\n\n🎱 Numéro : {num} {color}\n🎯 Mise : {mise_couleur}\n\n❌ Perdu... -{bet:.2f}{CURRENCY}\n💰 Solde : {bal2:.2f}{CURRENCY}"
    return msg, color == mise_couleur
```

