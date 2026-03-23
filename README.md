# 📊 Planning & Payment System

Асинхронний сервіс на **FastAPI** для обліку фінансових планів, кредитів та платежів. Проєкт автоматизує рутину завантаження даних та надає API для аналітики "план-факт". 

Тепер проєкт повністю контейнеризований і має чіткий розподіл бізнес-логіки.

## 🚀 Основні фішки
* **⚡ Async First**: Повністю асинхронний стек (**FastAPI + SQLAlchemy 2.0 + aiomysql**).
* **🤖 Smart Auto-Import**: 
    * Перевіряє базу на порожнечу перед імпортом (Idempotency).
    * Чистить "сміття" та NaN з Excel/CSV за допомогою **Pandas**.
* **🏗 Service Layer**: Математичні розрахунки аналітики винесені в окремий сервіс для кращої підтримки.
* **🐳 Docker Ready**: Готова інфраструктура з автоматичним очікуванням готовності БД.
* **🛡 Надійність**: Валідація даних через **Pydantic** та обмеження на рівні БД (Foreign Keys).
* **🐍 Python 3.13 Ready**.

---

## 🛠 Технологічний стек
* **Framework**: FastAPI
* **Database**: MySQL 8.0 (через асинхронний драйвер `aiomysql`)
* **ORM**: SQLAlchemy 2.0 (Async)
* **Infrastructure**: Docker & Docker Compose
* **Data Processing**: Pandas & Numpy
* **Testing**: Pytest (Asyncio mode)

---

## 📂 Структура проєкту
```text
├── app/
│   ├── main.py          # Точка входу, Lifespan та логування
│   ├── database.py      # Налаштування асинхронного Engine та Session
│   ├── models.py        # SQLAlchemy моделі (таблиці)
│   ├── schemas.py       # Pydantic схеми (валідація)
│   ├── services/        # Бізнес-логіка (AnalyticsService)
│   ├── reader.py        # Модуль інтелектуального імпорту CSV
│   ├── routes.py        # Логіка API ендпоінтів та фіксація схем
│   └── tests/           # Асинхронні тести
├── scripts/
│   └── entrypoint.sh    # Скрипт синхронізації запуску Docker
├── data_csv/            # Папка з вихідними даними (Plans, Credits, etc.)
├── Dockerfile           # Конфігурація образу додатка
└── docker-compose.yml   # Оркестрація контейнерів (App + DB)
```

---

## ⚙️ Швидкий старт (через Docker) — Рекомендовано

Це найшвидший спосіб запустити систему з усіма залежностями та базою даних.

1. **Налаштуйте `.env`**:
   Створіть файл `.env` у корені проєкту:
   ```env
   user=user
   password=password
   db=finance_db
   host=db
   ```

2. **Запустіть контейнери**:
   ```bash
   docker compose up --build
   ```
   *Додаток автоматично зачекає на готовність MySQL, запустить імпорт даних із `data_csv` та підніме API.*

---

## 🛠 Локальний запуск (без Docker)

1. **Підготовка**:
   ```bash
   git clone <your-repo-url>
   cd planning_payment
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **База даних**:
   Створіть базу в MySQL та пропишіть шлях у `.env` або `app/database.py`:
   `DATABASE_URL = "mysql+aiomysql://user:password@localhost/your_db_name"`

3. **Запуск**:
   ```bash
   fastapi dev
   ```

---

## 🧪 Тестування
Ми використовуємо **pytest** для перевірки асинхронної логіки:
```bash
pytest app/tests/test.py
```

---

## 📋 Особливості логування та імпорту
* **Logging**: Усі важливі події (старт додатка, успішний імпорт рядків, помилки валідації) логуються в консоль у структурованому форматі.
* **Import Idempotency**: Якщо таблиця вже містить записи, автоімпорт пропустить цей файл, щоб не порушити цілісність.
* **Analytics**: Розрахунки Performance (план/факт) та Share of Year виконуються в реальному часі через `AnalyticsService` з автоматичною валідацією через Pydantic у роутах.

---
