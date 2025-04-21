from flask import Blueprint

# Создаем blueprint
api_blueprint = Blueprint('api', __name__)

# Импортируем маршруты ПОСЛЕ создания blueprint
from . import routes