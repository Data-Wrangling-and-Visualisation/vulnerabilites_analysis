import os
from flask import Flask
from dotenv import load_dotenv

# Инициализация
load_dotenv()
app = Flask(__name__, 
           static_folder='frontend/static',
           template_folder='frontend/templates')

# Конфигурация
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация DB
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Импорт моделей и роутов
from backend.models.vulnerabilities import Vulnerability
from backend.api.routes import init_api

init_api(app)  # Инициализация API

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)