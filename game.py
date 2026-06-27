```python
import random
import json
from datetime import datetime, timedelta

═══════════════════════════════════════
CONFIG
═══════════════════════════════════════
START_BALANCE = 0.0
CASHBACK_PERCENT = 0.05
CURRENCY = "€"

DB_FILE = "gamecash_db.json"

═══════════════════════════════════════
DATA
═══════════════════════════════════════
game_stats = {}

slots_icons = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣", "⭐"]
slots_payouts = {
    (0,0,0): 5, (1,1,1): 5, (2,2,2): 5, (3,3,3): 5,
    (4,4,4): 10, (5,5,5): 15, (6,6,6): 50, (7,7,7): 100,
}

roulette_numbers = list(range(37))
roulette_colors = {0: "green"}
for i in range(1, 37):
    if 1 <= i <= 10:
        roulette_colors[i] = "red" if i % 2 == 1 else "black"
    elif 11 <= i <= 18:
        roulette_colors[i] = "black" if i % 2 == 1 else "red"
    elif 19 <= i <= 28:
        roulette_colors[i] = "red" if i % 2 == 1 else "black"
    else:
        roulette_colors[i] = "black" if i % 2 == 1 else "red"

dice_values = [1, 2, 3, 4, 5, 6]

═══════════════════════════════════════
DB helpers
═══════════════════════════════════════
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
    return float(db.get(uid, {}).get("balance", START_BALANCE))

def set_balance(user_id, amount):
    db = _load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": START_BALANCE, "deposited": 0}
    db[uid]["balance"] = float(amount)
    _save_db(db)

def add_balance(user_id, amount):
    bal = get_balance(user_id) + amount
    set_balance(user_id, bal)
    return bal

═══════════════════════════════════════
SLOTS
═══════════════════════════════════════
def jouer_slots(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", False

    bal = add_balance(user_id, -bet)
    r1, r2, r3 = [random.randint(0, len(slots_icons)-1) for _ in range(3)]

    result_line = f"| {slots_icons[r1]} | {slots_icons[r2]} | {slots_icons[r3]} |"
    multiplier = slots_payouts.get((r1, r2, r3), 0)
    win = bet * multiplier

    if win > 0:
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = (
            f"🎰 Slots\n\n"
            f"{result_line}\n\n"
            f"✅ Gagné ! +{win:.2f}{CURRENCY}\n"
            f"💰 Nouveau solde : {bal2:.2f}{CURRENCY}"
        )
    else:
        bal2 = get_balance(user_id)
        msg = (
            f"🎰 Slots\n\n"
            f"{result_line}\n\n"
            f"❌ Perdu... -{bet:.2f}{CURRENCY}\n"
            f"💰 Nouveau solde : {bal2:.2f}{CURRENCY}"
        )
    return msg, win > 0

═══════════════════════════════════════
DICE═══════════════════════════════════════
def jouer_dice(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", False

    bal = add_balance(user_id, -bet)
    dice = random.randint(1, 6)
    target = random.randint(3, 4)  # 50/50 environ

    if dice >= target:
        win = bet * 1.8
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = (
            f"🎲 Dice\n\n"
            f"🎲 Résultat : {dice}\n"
            f"🎯 Cible : {target}+\n\n"
            f"✅ Gagné ! +{win:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    else:
        bal2 = get_balance(user_id)
        msg = (
            f"🎲 Dice\n\n"
            f"🎲 Résultat : {dice}\n"
            f"🎯 Cible : {target}+\n\n"
            f"❌ Perdu... -{bet:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    return msg, dice >= target

═══════════════════════════════════════
BACCARAT (simplifié)
═══════════════════════════════════════
def jouer_baccarat(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", False

    bal = add_balance(user_id, -bet)
    player = random.randint(0, 9)
    banker = random.randint(0, 9)

    if player > banker:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = (
            f"🃏 Baccarat\n\n"
            f"👤 Joueur : {player}\n"
            f"🏦 Banque : {banker}\n\n"
            f"✅ Joueur gagne ! +{win:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    elif banker > player:
        bal2 = get_balance(user_id)
        msg = (
            f"🃏 Baccarat\n\n"
            f"👤 Joueur : {player}\n"
            f"🏦 Banque : {banker}\n\n"
            f"❌ Banque gagne... -{bet:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    else:
        add_balance(user_id, bet)
        bal2 = get_balance(user_id)
        msg = (
            f"🃏 Baccarat\n\n"
            f"👤 Joueur : {player}\n"
            f"🏦 Banque : {banker}\n\n"
            f"🤝 Égalité ! Remboursé\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    return msg, player > banker

═══════════════════════════════════════
COINFLIP
═══════════════════════════════════════
def jouer_coinflip(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", False

    bal = add_balance(user_id, -bet)
    result = random.choice(["Pile", "Face"])
    user_choice = random.choice(["Pile", "Face"])  # aleatoire pour demo

    if result == user_choice:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = (
            f"🪙 Pile ou Face\n\n"
            f"🪙 Résultat : {result}\n"
            f"🎯 Ton choix : {user_choice}\n\n"
            f"✅ Gagné ! +{win:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    else:
        bal2 = get_balance(user_id)
        msg = (
            f"🪙 Pile ou Face\n\n"
            f"🪙 Résultat : {result}\n"
            f"🎯 Ton choix : {user_choice}\n\n"
            f"❌ Perdu... -{bet:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    return msg, result == user_choice═══════════════════════════════════════
ROULETTE
═══════════════════════════════════════
def jouer_roulette(user_id, bet):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! ({bal:.2f}{CURRENCY})", False

    bal = add_balance(user_id, -bet)
    num = random.randint(0, 36)
    color = roulette_colors[num]

Mise sur rouge/noir aléatoire pour demo
    user_color = random.choice(["red", "black"])

    if color == user_color:
        win = bet * 1.9
        add_balance(user_id, win)
        bal2 = get_balance(user_id)
        msg = (
            f"🔴⚫ Roulette\n\n"
            f"🎱 Numéro : {num} ({color})\n"
            f"🎯 Mise : {user_color}\n\n"
            f"✅ Gagné ! +{win:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    else:
        bal2 = get_balance(user_id)
        msg = (
            f"🔴⚫ Roulette\n\n"
            f"🎱 Numéro : {num} ({color})\n"
            f"🎯 Mise : {user_color}\n\n"
            f"❌ Perdu... -{bet:.2f}{CURRENCY}\n"
            f"💰 Solde : {bal2:.2f}{CURRENCY}"
        )
    return msg, color == user_color
```
