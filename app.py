import os
from flask import Flask, render_template, request, g
from backend import db
from backend.api import api_blueprint
from config import Config

# Указываем пути к шаблонам и статике
BASE = os.path.dirname(__file__)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE, 'frontend', 'templates'),
    static_folder=os.path.join(BASE, 'frontend', 'static')
)

# Конфигурация
app.config.from_object(Config)

# Инициализация SQLAlchemy
db.init_app(app)

# Blueprint API
app.register_blueprint(api_blueprint, url_prefix='/api')

# Определение языка
@app.before_request
def get_language():
    g.lang = request.args.get('lang', 'ru')

# Хелпер для render_template + lang
def render_with_lang(template_name):
    return render_template(template_name, lang=g.lang)

# Роуты
@app.route('/')
def index():
    return render_with_lang('index.html')

@app.route('/dashboard')
def dashboard():
    return render_with_lang('dashboard.html')

@app.route('/trend')
def trend():
    return render_with_lang('trend.html')

@app.route('/cwe')
def cwe():
    return render_with_lang('cwe.html')

@app.route('/team')
def team_page():
    return render_with_lang('team.html')

@app.route('/vendors')
def vendors():
    return render_with_lang('vendors.html')

@app.route('/info')
def info_page():
    return render_with_lang('info.html')

# Запуск
if __name__ == '__main__':
    print(f"Template folder path: {app.template_folder}")
    print(f"Files in template folder: {os.listdir(app.template_folder)}")
    app.run(debug=True)
