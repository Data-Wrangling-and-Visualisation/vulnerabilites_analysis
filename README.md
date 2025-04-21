# CVE Vulnerability Dashboard

Интерактивный дашборд уязвимостей CVE на Flask + D3.js

---

## Описание

Этот проект представляет собой веб‑приложение для визуализации данных об уязвимостях из Национальной Базы Уязвимостей (NVD).  
Основные возможности:

- **Импорт** свежих CVE из NVD API по расписанию  
- **API** на Flask + SQLite/SQLAlchemy с фильтрами по дате, severity, вектору атаки, CWE, вендору  
- **Фронтенд** на D3.js:  
  - Donut‑диаграмма распределения severity  
  - Линейные графики CVSS во времени  
  - Горизонтальные и вертикальные бары (Attack Vector, Top 10 CWE)  
  - Страницы детализации по CWE, вендору, общему тренду  
- **Интерактивность**: фильтры, тултипы, анимированные переходы  
- **Адаптивный дизайн**: карточки меняют расположение на мобильных

---

## Содержание репозитория

```
.
├── app.py                      # основной Flask‑приложение
├── requirements.txt            # Python‑зависимости
├── Procfile                    # для Heroku
├── backend/                    # код бэкенда, models, db
│   ├── __init__.py
│   ├── models.py
│   └── fetcher.py              # сбор данных из NVD
└── frontend/
    ├── templates/              # Jinja-шаблоны
    │   ├── base.html
    │   ├── index.html
    │   ├── dashboard.html
    │   ├── vendors.html
    │   ├── cwe.html
    │   └── trend.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            ├── app.js
            ├── vendors.js
            ├── cwe.js
            └── trend.js
```

---

## Требования

- Python 3.10+  
- Node.js/npm (для локального шаринга через LocalTunnel)  
- Git

---

## Установка и запуск локально

1. **Клонируйте репозиторий**  
   ```bash
   git clone https://github.com/Data-Wrangling-and-Visualisation/vulnerabilites_analysis
   cd ВАШ_РЕПО
   ```

2. **Создайте и активируйте виртуальное окружение**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   # .venv\Scripts\Activate.ps1   # Windows PowerShell
   ```

3. **Установите зависимости**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Экспорт переменных окружения**  
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   # Windows CMD:
   # set FLASK_APP=app.py
   # set FLASK_ENV=development
   ```

5. **Запустите сервер**  
   ```bash
   python -m flask run --host=0.0.0.0 --port=5000
   ```
   Приложение будет доступно по http://localhost:5000/

---

## Шаринг наружу (LocalTunnel)

Чтобы быстро поделиться локальным сервером по публичному URL:

1. Установите LocalTunnel (если ещё не):
   ```bash
   npm install -g localtunnel
   ```
2. Запустите:
   ```bash
   lt --port 5000 --subdomain myvulndash --no-auth
   ```
3. Получите URL вида `https://myvulndash.loca.lt` и отправьте коллегам.

---

## Деплой на Heroku (опционально)

1. **Создайте Procfile** (если ещё нет):
   ```
   web: gunicorn app:app
   ```
2. **Подготовьте requirements.txt**:
   ```bash
   pip freeze > requirements.txt
   ```
3. **Логин и деплой**:
   ```bash
   heroku login
   git init
   heroku create your-app-name
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   heroku ps:scale web=1
   heroku open
   ```

---

## Структура API

- **`GET /api/vulnerabilities`**  
  Параметры (optional):  
  `date_from=YYYY-MM-DD`, `date_to=…`, `severity=CRITICAL|HIGH|…`,  
  `attack_vector=NETWORK|LOCAL|…`, `cwe=CWE-79`, `vendor=Microsoft`
- **`GET /api/stats`**  
  Возвращает время последнего обновления данных.

---
