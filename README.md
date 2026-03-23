# 📊 Planning & Payment System

Асинхронний сервіс на **FastAPI** для обліку фінансових планів, кредитів та платежів. Проєкт автоматизує рутину завантаження даних та надає API для аналітики "план-факт".

## 🚀 Основні фішки

* **⚡ Async First:** Повністю асинхронний стек (FastAPI + SQLAlchemy 2.0 + aiomysql).
* **🤖 Smart Auto-Import:** 
    * Перевіряє базу на порожнечу перед імпортом (Idempotency).
    * Чистить "сміття" та `NaN` з Excel/CSV (перетворює в `NULL`).
* **🛡 Надійність:** Валідація даних через Pydantic та обмеження на рівні БД (Foreign Keys).
* **🐍 Python 3.13 Ready**

---

## 🛠 Технологічний стек

* **Framework:** FastAPI
* **Database:** MySQL (через асинхронний драйвер `aiomysql`)
* **ORM:** SQLAlchemy 2.0 (Async)
* **Data Science:** Pandas & Numpy (для обробки сирих CSV)
* **Testing:** Pytest (Asyncio mode)

---

## 📂 Структура проєкту

```text
├── app/
│   ├── main.py          # Точка входу, Lifespan та роути
│   ├── database.py      # Налаштування асинхронного Engine та Session
│   ├── models.py        # SQLAlchemy моделі (таблиці)
│   ├── schemas.py       # Pydantic схеми (валідація)
│   ├── reader.py        # Модуль інтелектуального імпорту CSV
│   ├── routes.py        # Логіка API ендпоінтів
│   └── tests/               # Асинхронні тести
├── data_csv/            # Папка з вихідними даними (Dictionary, Users, Plans, etc.)
├── .gitignore           # Ігнорування venv, ключів та локальних даних
└── pytest.ini           # Конфігурація тестування
```

---

## ⚙️ Швидкий старт

### 1. Підготовка середовища
```bash
# Клонуємо репозиторій
git clone <your-repo-url>
cd planning_payment
# Створюємо та активуємо venv
python3.13 -m venv .venv
source .venv/bin/activate

# Встановлюємо залежності
pip install -r requirements.txt
```

### 2. Налаштування бази даних
Створи базу в MySQL та пропиши шлях у `app/database.py`:
```python
DATABASE_URL = "mysql+aiomysql://user:password@localhost/your_db_name"
```

### 3. Запуск
```bash
fastapi dev
```
*При старті додаток автоматично перевірить папку `data_csv` і заповнить порожні таблиці.*

---

## 🧪 Тестування
Ми використовуємо `pytest` для перевірки асинхронної логіки:
```bash
pytest app/tests/test.py
```

---

## 📋 Особливості імпорту даних
Система очікує CSV-файли в папці `data_csv`.
* **Дублікати:** Якщо таблиця вже містить записи, автоімпорт пропустить цей файл, щоб не порушити цілісність.

---