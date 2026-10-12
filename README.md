# MinterShopBot 1.7

## Почему «виснут» /menu и кнопки

В логах это не баг команд:

```
TelegramConflictError: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**Одновременно запущены 2+ копии бота с одним токеном.**
Они отбирают апдейты друг у друга → команды и inline «через раз» или молчат.

### Что сделать на хостинге

1. Остановить **все** процессы/контейнеры этого бота.
2. Проверить, что реплик **ровно 1** (scale = 1).
3. Запустить **один** `python bot.py`.
4. В логе **не** должно быть Conflict каждые 5 секунд.

В 1.7:
- файл-лок `data/bot.lock` (второй процесс на том же диске не стартует);
- в консоль явное предупреждение при Conflict.

## Команды
/start /menu /settings /appeal
