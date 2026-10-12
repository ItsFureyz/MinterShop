# -*- coding: utf-8 -*-
"""JSON-хранилище: отзывы, ЧС, чеки, премиум-юзеры, балансы."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from config import DATA_DIR, OWNER_IDS, ADMIN_IDS

def _path(name: str) -> Path:
    return DATA_DIR / name


def _load(name: str, default: Any):
    p = _path(name)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(name: str, data: Any) -> None:
    _path(name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Users / balance ──────────────────────────────────────────

def get_user(uid: int) -> dict:
    users = _load("users.json", {})
    key = str(uid)
    if key not in users:
        users[key] = {
            "stars": 0.0,
            "purchases": 0,
        }
        _save("users.json", users)
    return users[key]


def set_user(uid: int, data: dict) -> None:
    users = _load("users.json", {})
    users[str(uid)] = data
    _save("users.json", users)


def add_stars(uid: int, amount: float) -> float:
    u = get_user(uid)
    u["stars"] = float(u.get("stars", 0)) + amount
    set_user(uid, u)
    return u["stars"]


# ── Reviews (forwarded messages) ─────────────────────────────
# item: {id, chat_id, message_id, added_by, added_at}

def list_reviews() -> list:
    return _load("reviews.json", [])


def add_review(chat_id: int, message_id: int, added_by: int) -> dict:
    items = list_reviews()
    item = {
        "id": len(items) + 1,
        "chat_id": chat_id,
        "message_id": message_id,
        "added_by": added_by,
        "added_at": int(time.time()),
    }
    items.append(item)
    _save("reviews.json", items)
    return item


def get_review(num: int) -> Optional[dict]:
    for r in list_reviews():
        if r.get("id") == num:
            return r
    return None


def delete_review(num: int) -> bool:
    items = list_reviews()
    new = [r for r in items if r.get("id") != num]
    if len(new) == len(items):
        return False
    # re-number
    for i, r in enumerate(new, 1):
        r["id"] = i
    _save("reviews.json", new)
    return True


# ── Blacklist ────────────────────────────────────────────────

def list_blacklist() -> list:
    return _load("blacklist.json", [])


def is_blacklisted(uid: int) -> bool:
    return any(x.get("user_id") == uid for x in list_blacklist())


def add_blacklist(uid: int, reason: str = "", by: int = 0) -> bool:
    items = list_blacklist()
    if any(x.get("user_id") == uid for x in items):
        return False
    items.append({
        "user_id": uid,
        "reason": reason,
        "by": by,
        "at": int(time.time()),
    })
    _save("blacklist.json", items)
    return True


def remove_blacklist(uid: int) -> bool:
    items = list_blacklist()
    new = [x for x in items if x.get("user_id") != uid]
    if len(new) == len(items):
        return False
    _save("blacklist.json", new)
    return True


# ── Premium users (can create deal checks) ───────────────────

def list_premium_users() -> list:
    return _load("premium_users.json", [])


def can_create_deal(uid: int) -> bool:
    if uid in OWNER_IDS or uid in ADMIN_IDS:
        return True
    return any(x.get("user_id") == uid for x in list_premium_users())


def add_premium_user(uid: int, by: int = 0) -> bool:
    items = list_premium_users()
    if any(x.get("user_id") == uid for x in items):
        return False
    items.append({"user_id": uid, "by": by, "at": int(time.time())})
    _save("premium_users.json", items)
    return True


def remove_premium_user(uid: int) -> bool:
    items = list_premium_users()
    new = [x for x in items if x.get("user_id") != uid]
    if len(new) == len(items):
        return False
    _save("premium_users.json", new)
    return True


# ── Checks ───────────────────────────────────────────────────
# type: friend | deal
# status: pending | accepted | rejected | completed | cancelled

def list_checks() -> list:
    return _load("checks.json", [])


def save_checks(items: list) -> None:
    _save("checks.json", items)


def create_check(
    creator_id: int,
    check_type: str,
    stars: float,
    nft_link: str = "",
) -> dict:
    items = list_checks()
    check = {
        "id": str(uuid.uuid4())[:8],
        "type": check_type,
        "creator_id": creator_id,
        "stars": float(stars),
        "nft_link": nft_link or "",
        "status": "pending",
        "acceptor_id": None,
        "created_at": int(time.time()),
    }
    items.append(check)
    save_checks(items)
    return check


def get_check(check_id: str) -> Optional[dict]:
    for c in list_checks():
        if c.get("id") == check_id:
            return c
    return None


def update_check(check_id: str, **kwargs) -> Optional[dict]:
    items = list_checks()
    for c in items:
        if c.get("id") == check_id:
            c.update(kwargs)
            save_checks(items)
            return c
    return None


def delete_check(check_id: str) -> bool:
    items = list_checks()
    new = [c for c in items if c.get("id") != check_id]
    if len(new) == len(items):
        return False
    save_checks(new)
    return True


def checks_for_user(uid: int) -> list:
    """Чеки, которые пользователь принял или создал."""
    return [
        c for c in list_checks()
        if c.get("acceptor_id") == uid or c.get("creator_id") == uid
    ]


def deal_checks_all() -> list:
    return [c for c in list_checks() if c.get("type") == "deal"]
