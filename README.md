# Minter Shop Bot (каркас по логу CopyBot)

Telegram-бот на **aiogram 3** по структуре `@MinterShop_Bot` из лога CopyBot.

## Что есть сейчас

| Функция | Статус |
|---------|--------|
| `/start` → стикер + фото + приветствие | ✅ |
| Главное меню (inline) | ✅ |
| Вывод звёзд (экран Fragment) | ✅ UI, без реального вывода |
| Автоскупщик (вкл/выкл) | ✅ флаг в памяти |
| Кошелёк (баланс) | ✅ in-memory |
| Магазин → Премиум (3/6/12 мес) | ✅ UI, «через 21 день» |
| Магазин → Подарки | ⚠️ заглушка |
| Пополнить баланс | ⚠️ заглушка (без оплаты) |
| Создать чек (switch_inline) | ✅ кнопка |
| Веб-Кошелек (WebApp) | 🔗 кнопка с URL из `.env` (сайт **не** входит в архив) |
| База данных / реальные звёзды | ❌ только dict в памяти |
| Платежи | ❌ |

## Установка

```bash
cd MinterShopBot
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# отредактируй .env → BOT_TOKEN=...
python bot.py
```

Токен: [@BotFather](https://t.me/BotFather) → `/newbot`.

---

## Как отправить определённый стикер после /start

Бот **сначала** шлёт стикер, **потом** фото с меню.

### Способ A — `file_id` (удобнее)

1. Временно добавь в `handlers/start.py` (или отдельным скриптом) лог:
   ```python
   @router.message(F.sticker)
   async def catch_sticker(message: Message):
       print(message.sticker.file_id)
       await message.answer(f"<code>{message.sticker.file_id}</code>")
   ```
2. Запусти бота, **перешли ему нужный стикер** из любого пака.
3. Скопируй `file_id` в `.env`:
   ```
   START_STICKER_ID=CAACAgIAAxkBAAI...длинный_id...
   ```
4. Убери временный хендлер, перезапусти бота.

`file_id` привязан к **твоему** боту: чужой id от другого бота не сработает.

### Способ B — файл

1. Сохрани стикер как `.webp` или `.tgs` в `media/start_sticker.webp`.
2. В `.env`:
   ```
   START_STICKER_FILE=media/start_sticker.webp
   ```

Если оба пустые — стикер просто не отправляется, остальное работает.

---

## Сайт в Telegram-боте позже

**Да, можно.** Кнопка «💻 Веб-Кошелек» — это **Telegram Web App**: бот открывает URL внутри Telegram.

### Как это обычно работает на одном хосте

```
VPS / сервер
├── nginx (HTTPS, порт 443)
│   ├── /          → статика сайта (React/Vue/HTML)
│   └── /webhook   → опционально webhook бота
└── python bot.py  (long polling или webhook)
```

1. **HTTPS обязателен** для WebApp (Let's Encrypt).
2. В `.env` ставишь `WEBAPP_URL=https://твой-домен.ru/app`.
3. Сайт использует [Telegram WebApp JS SDK](https://core.telegram.org/bots/webapps):
   - `window.Telegram.WebApp` — user id, theme, `initData` для проверки на бэкенде.
4. Бот и сайт **не обязаны** быть одним процессом: сайт — nginx + HTML/Node, бот — Python. Связь через API (баланс, чеки) по `user_id` из `initData`.

Пока сайтовую часть **не делаем** — кнопка ведёт на `WEBAPP_URL` из `.env` (по умолчанию example.com). Когда скажешь — можно встроить свой фронт.

---

## Структура

```
MinterShopBot/
  bot.py              — точка входа
  config.py           — токен, стикер, URL, «БД»
  keyboards.py        — все inline-клавиатуры
  handlers/
    start.py          — /start + стикер
    callbacks.py      — экраны меню
  media/welcome.jpg   — картинка приветствия из лога
  .env.example
  requirements.txt
  README.md
```

## Callback map (из лога)

| data | Экран |
|------|--------|
| `withdraw` | Нужен Fragment |
| `autobuy` / `autobuy_change` | Автоскуп |
| `wallet` | Кошелёк |
| `shop` | Магазин |
| `premium` | Срок подписки |
| `wait_21_days` | «Откроется через 21 день» |
| `gifts` | заглушка |
| `topup` | Пополнение (заглушка) |
| `topup_back` | Главное меню |
