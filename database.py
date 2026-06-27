import json, os

DB_FILE = "players.json"

def _load():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_player(user_id):
    db = _load()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 0, "total_bet": 0, "total_loss": 0, "games_played": 0, "total_won": 0, "username": ""}
        _save(db)
    return db[uid]

def update_player(user_id, username=""):
    db = _load()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 0, "total_bet": 0, "total_loss": 0, "games_played": 0, "total_won": 0, "username": ""}
    if username:
        db[uid]["username"] = username
    _save(db)

def update_balance(user_id, amount):
    db = _load()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"balance": 0, "total_bet": 0, "total_loss": 0, "games_played": 0, "total_won": 0, "username": ""}
    db[uid]["balance"] += amount
    db[uid]["games_played"] += 1
    if amount < 0:
        db[uid]["total_loss"] += abs(amount)
        db[uid]["total_bet"] += abs(amount)
    else:
        db[uid]["total_won"] += amount
    _save(db)

def apply_cashback(user_id):
    db = _load()
    uid = str(user_id)
    if uid not in db:
        return 0
    loss = db[uid].get("total_loss", 0)
    if loss <= 0:
        return 0
    cb = int(loss * CASHBACK_PERCENT / 100)
    if cb > 0:
        db[uid]["balance"] += cb
        db[uid]["total_loss"] = 0
        _save(db)
    return cb

def get_level(balance):
    prev = "🟤 Fer"
    for name, threshold in LEVELS.items():
        if balance >= threshold:
            prev = name
        else:
            break
    return prev

def get_next_level_info(balance):
    prev_name, prev_thr = "🟤 Fer", 0
    for name, threshold in LEVELS.items():
        if balance >= threshold:
            prev_name, prev_thr = name, threshold
        else:
            need = threshold - balance
            return name, need, threshold
    return None, 0, 0

def get_leaderboard(top=10):
    db = _load()
    sorted_players = sorted(db.items(), key=lambda x: x[1].get("balance", 0), reverse=True)
    lb = []
    for uid, data in sorted_players[:top]:
        bal = data.get("balance", 0)
        name = data.get("username", f"User{uid[:4]}")
        level = get_level(bal)
        lb.append((name, bal, level))
    return lb
