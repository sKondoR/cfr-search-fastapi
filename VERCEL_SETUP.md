# Настройка Vercel для RusClimbing API

## Необходимые шаги

### 1. Переменные окружения

Добавьте следующие переменные окружения в настройках проекта на Vercel:

#### Обязательные:

- `DATABASE_URL` - URL подключения к базе данных PostgreSQL (например: `postgresql+asyncpg://user:password@host:5432/dbname`)

#### Необязательные (можно оставить значения по умолчанию):

- `BASE_URL` - Базовый URL для парсинга соревнований (по умолчанию: `https://www.rusclimbing.ru/competitions/`)
- `LIVE_RESULTS_BASE_URL` - Базовый URL для получения результатов (по умолчанию: `https://c-f-r.ru/live/`)
- `LIVE_RESULTS_PATH` - Путь к файлу результатов (по умолчанию: `l_q_f13.html`)
- `EVENT_NAME` - Фильтр по названию события (по умолчанию: `Всероссийские соревнования`)
- `EVENT_YEAR` - Фильтр по году (по умолчанию: `2026`)
- `EVENT_GROUP` - Фильтр по группе (по умолчанию: `13-14`)
- `REJECTED_WORDS` - Слова, которые отфильтровывают события (по умолчанию: `["ОТМЕНЕНО", "ОТМЕНЕНЫ"]`)
- `ORIGINS` - Список разрешённых CORS origins (по умолчанию: `["*"]`)

### 2. Деплой

После добавления переменных окружений:

1. Зафиксируйте изменения:

   ```bash
   git add .
   git commit -m "fix: configure Vercel deployment"
   git push
   ```

2. Vercel автоматически запустит сборку и деплой

3. После завершения деплоя проверьте логи, чтобы убедиться, что приложение запустилось успешно

## Структура проекта

```
rusclimbing-search/
├── app/
│   ├── api/
│   │   ├── main.py          # Точка входа FastAPI приложения
│   │   └── v1/
│   │       └── routes/      # API маршруты
│   ├── core/
│   │   ├── config.py        # Конфигурация приложения
│   │   └── permissions.py   # Проверка прав доступа
│   └── db/
│       └── db.py            # Работа с базой данных
├── vercel.json              # Конфигурация Vercel
├── .vercelignore            # Исключения при деплое
├── pyproject.toml           # Зависимости Python
└── package.json             # Конфигурация проекта
```

## Проверка работы

После деплоя проверьте:

1. **Корневой endpoint**: `https://your-project.vercel.app/`
2. **Health check**: `https://your-project.vercel.app/health`
3. **Swagger документация**: `https://your-project.vercel.app/docs`

## Логи и отладка

Если возникают ошибки:

1. Перейдите в раздел **Logs** на Vercel Dashboard
2. Проверьте логи сборки
3. Проверьте логи запущенного сервера
4. Убедитесь, что все переменные окружения добавлены корректно

## Дополнительные ресурсы

- [FastAPI на Vercel](https://vercel.com/docs/frameworks/backend/fastapi)
- [Переменные окружения на Vercel](https://vercel.com/docs/concepts/projects/environment-variables)
- [Python Runtime на Vercel](https://vercel.com/docs/concepts/functions/runtimes/python)
