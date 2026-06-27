```python
import random
import json
from datetime import datetime, timedelta

============ CONFIG ============
START_BALANCE = 0.0
CASHBACK_PERCENT = 0.05
CURRENCY = "€"

============ DATA ============
game_stats = {}  # user_id -> {"wins": int, "losses": int, "total_bet": float, "total_win": float, "last_bet_date": str}

slots_icons = ["🍒", "🍋", "🍊", "🍇", "🔔", "💎", "7️⃣", "⭐"]
slots_payouts = {
    (0,0,0): 5, (1,1,1): 5, (2,2,2): 5, (3,3,3): 5,
    (4,4,4): 10, (5,5,5): 15, (6,6,6): 50, (7,7,7): 100,
}

roulette_numbers = list(range(37))
roulette_colors = {0: "green"}
for i in range(1, 37):
    if i == 0:
        roulette_colors[i] = "green"
    elif 1 <= i <= 10:
        roulette_colors[i] = "red" if i % 2 == 1 else "black"
    elif 11 <= i <= 18:
        roulette_colors[i] = "black" if i % 2 == 1 else "red"
    elif 19 <= i <= 28:
        roulette_colors[i] = "red" if i % 2 == 1 else "black"
    else:
        roulette_colors[i] = "black" if i % 2 == 1 else "red"

============ PLAYER ============
def load_players():
    try:
        with open("players.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_players(players):
    with open("players.json", "w") as f:
        json.dump(players, f, indent=2)

def get_balance(user_id):
    players = load_players()
    uid = str(user_id)
    if uid not in players:
        players[uid] = {"balance": START_BALANCE, "username": "", "joined": str(datetime.now())}
        save_players(players)
    return players[uid]["balance"]

def set_balance(user_id, amount):
    players = load_players()
    uid = str(user_id)
    if uid in players:
        players[uid]["balance"] = round(amount, 2)
        save_players(players)
    return round(amount, 2)

def add_balance(user_id, amount):
    bal = get_balance(user_id)
    new_bal = bal + amount
    return set_balance(user_id, new_bal)

============ GAMES ============

def play_slots(user_id, bet):
    """Slot machine, returns (result_string, win_amount)"""
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! Tu as {bal:.2f}{CURRENCY}", 0

    add_balance(user_id, -bet)

    reel1 = random.choice(slots_icons)
    reel2 = random.choice(slots_icons)
    reel3 = random.choice(slots_icons)

Check if all three match
    result_tuple = (slots_icons.index(reel1), slots_icons.index(reel2), slots_icons.index(reel3))
    multiplier = slots_payouts.get(result_tuple, 0)

    if multiplier > 0 and reel1 == reel2 == reel3:
        win = round(bet * multiplier, 2)
        add_balance(user_id, win)
        return (
            f"🎰 SLOTS\n"
            f"┌─────┬─────┬─────┐\n"
            f"│  {reel1}  │  {reel2}  │  {reel3}  │\n"
            f"└─────┴─────┴─────┘\n\n"
            f"🔥 JACKPOT ! x{multiplier}\n"
            f"💰 +{win:.2f}{CURRENCY}",
            win
        )
    else:
        return (
            f"🎰 SLOTS\n"
            f"┌─────┬─────┬─────┐\n"
            f"│  {reel1}  │  {reel2}  │  {reel3}  │\n"
            f"└─────┴─────┴─────┘\n\n"
            f"😔 Perdu... -{bet:.2f}{CURRENCY}",
            0
        )

def play_roulette(user_id, bet, bet_type, bet_value):
    """Roulette game. bet_type: 'number', 'color', 'odd_even'"""
    bal = get_balance(user_id)
    if bal < bet:return f"❌ Solde insuffisant ! Tu as {bal:.2f}{CURRENCY}", 0

    add_balance(user_id, -bet)
    result = random.choice(roulette_numbers)
    color = roulette_colors[result]
    win = 0
    status = "❌ Perdu"

    if bet_type == "number" and int(bet_value) == result:
        win = round(bet * 36, 2)
        status = "🔥 NUMÉRO DIRECT !"
    elif bet_type == "color" and bet_value == color:
        win = round(bet * 2, 2)
        status = "✅ Bonne couleur !"
    elif bet_type == "odd_even":
        if bet_value == "odd" and result % 2 == 1 and result != 0:
            win = round(bet * 2, 2)
            status = "✅ Impair gagne !"
        elif bet_value == "even" and result % 2 == 0 and result != 0:
            win = round(bet * 2, 2)
            status = "✅ Pair gagne !"

    if win > 0:
        add_balance(user_id, win)

    return (
        f"🎡 ROULETTE\n\n"
        f"Bille s'arrête sur... {result} {color}\n\n"
        f"{status}\n"
        f"{'💰 +' + str(win) + CURRENCY if win > 0 else f'😔 -{bet:.2f}' + CURRENCY}",
        win
    )

def play_dice(user_id, bet, prediction):
    """Dice game: prediction = 'over' or 'under', value = 50 (default)"""
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! Tu as {bal:.2f}{CURRENCY}", 0

    add_balance(user_id, -bet)
    roll = random.randint(1, 100)
    win = 0

    if prediction == "over" and roll > 50:
        win = round(bet * 1.96, 2)
        status = "✅ Plus de 50 !"
    elif prediction == "under" and roll <= 50:
        win = round(bet * 1.96, 2)
        status = "✅ Moins de 50 !"
    else:
        status = "❌ Perdu"

    if win > 0:
        add_balance(user_id, win)

    return (
        f"🎲 DICE\n\n"
        f"Résultat : {roll}\n"
        f"Prédiction : {prediction} 50\n\n"
        f"{status}\n"
        f"{'💰 +' + str(win) + CURRENCY if win > 0 else f'😔 -{bet:.2f}' + CURRENCY}",
        win
    )

def play_coinflip(user_id, bet, side):
    bal = get_balance(user_id)
    if bal < bet:
        return f"❌ Solde insuffisant ! Tu as {bal:.2f}{CURRENCY}", 0

    add_balance(user_id, -bet)
    result = random.choice(["pile", "face"])
    win = 0

    if side == result:
        win = round(bet * 1.96, 2)
        add_balance(user_id, win)
        status = f"✅ C'est {result} !"
    else:
        status = f"❌ C'est {result}..."

    return (
        f"🪙 PILE OU FACE\n\n"
        f"Résultat : {result}\n"
        f"Ton choix : {side}\n\n"
        f"{status}\n"
        f"{'💰 +' + str(win) + CURRENCY if win > 0 else f'😔 -{bet:.2f}' + CURRENCY}",
        win
    )

============ CASHBACK ============
def apply_cashback(user_id):
    """Apply 5% cashback on net losses"""
    stats = game_stats.get(str(user_id), {})
    if not stats:
        return None
    net = stats.get("total_bet", 0) - stats.get("total_win", 0)
    if net <= 0:
        return None
    cashback = round(net * CASHBACK_PERCENT, 2)
    add_balance(user_id, cashback)
    return cashback

============ STATS ============
def get_profile(user_id, username=""):
    bal = get_balance(user_id)
    stats = game_stats.get(str(user_id), {"wins": 0, "losses": 0, "total_bet": 0, "total_win": 0})
    return (
        f"👤 PROFIL\n\n"
        f"Nom : {username or 'Inconnu'}\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}\n"
        f"🏆 Victoires : {stats['wins']}\n"
        f"💀 Défaites : {stats['losses']}\n"f"📊 Total misé : {stats['total_bet']:.2f}{CURRENCY}\n"
        f"💵 Total gagné : {stats['total_win']:.2f}{CURRENCY}"
    )
```
# ============ BACCARAT ============
def creer_paquet():
    couleurs = ["♠", "♥", "♦", "♣"]
    valeurs = [("2",2),("3",3),("4",4),("5",5),("6",6),("7",7),("8",8),("9",9),("10",10),("Valet",0),("Dame",0),("Roi",0),("As",1)]
    return [f"{v[0]}{c}" for c in couleurs for v in valeurs], {f"{v[0]}{c}": v[1] for c in couleurs for v in valeurs}

def valeur_main(main, valeurs):
    total = sum(valeurs[c] for c in main) % 10
    return total

def jouer_baccarat(user_id, mise):
    bal = get_balance(user_id)
    if mise < 1 or mise > bal:
        return f"❌ Mise invalide (min 1{CURRENCY}, max {bal:.2f}{CURRENCY})", 0

    paquet, valeurs = creer_paquet()
    random.shuffle(paquet)

    # Distribution
    joueur = [paquet.pop(), paquet.pop()]
    banque = [paquet.pop(), paquet.pop()]

    v_joueur = valeur_main(joueur, valeurs)
    v_banque = valeur_main(banque, valeurs)

    # Règle du Baccarat (tirage automatique)
    if v_joueur <= 5:
        joueur.append(paquet.pop())
        v_joueur = valeur_main(joueur, valeurs)

    if v_banque <= 5:
        # Tirage banque selon règles
        if len(joueur) == 3:
            trois_carte = valeurs[joueur[2]]
            if trois_carte <= 7 and v_banque <= 5:
                banque.append(paquet.pop())
        else:
            banque.append(paquet.pop())
        v_banque = valeur_main(banque, valeurs)

    gain = 0
    # Le joueur mise sur "Joueur" (paiement 1:1)
    if v_joueur > v_banque:
        gain = mise
        result = "🏆 **Joueur gagne !**"
    elif v_banque > v_joueur:
        gain = -mise
        result = "🏆 **Banque gagne !**"
    else:
        result = "🤝 **Égalité** (remboursé)"
        gain = 0

    add_balance(user_id, gain)
    bal = get_balance(user_id)

    return (
        f"🃏 **Baccarat**\n\n"
        f"🧑 **Joueur :** {' '.join(joueur)} = {v_joueur}\n"
        f"🏦 **Banque :** {' '.join(banque)} = {v_banque}\n\n"
        f"{result}\n"
        f"{'✅ +' + str(gain) if gain > 0 else '❌ -' + str(abs(gain)) if gain < 0 else '↩️ 0'}{CURRENCY}\n"
        f"💰 Solde : {bal:.2f}{CURRENCY}"
    ), gain
