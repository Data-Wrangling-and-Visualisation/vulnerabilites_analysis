from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    return app