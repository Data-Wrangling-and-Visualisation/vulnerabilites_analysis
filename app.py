from flask import Flask, render_template
import os
from backend.api import api_blueprint

# Указываем правильный путь к шаблонам
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

# Конфигурация приложения
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Регистрация blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Проверка пути к шаблонам перед запуском
    print(f"Template folder path: {app.template_folder}")
    print(f"Files in template folder: {os.listdir(app.template_folder)}")
    app.run(debug=True)