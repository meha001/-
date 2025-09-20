__author__ = 'meha001'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # Исправленный импорт
from flask_security import SQLAlchemyUserDatastore, Security  # Исправленный импорт
from App import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

from App.models import User, Role, roles_users
from App.routes import api

# Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_blueprint=False)  # Исправленная инициализация

# init database data
try:
    with app.app_context():  # Добавлен контекст приложения
        db.create_all()
        # Проверяем, существуют ли уже пользователи и роли
        if not User.query.filter_by(username="test1").first():
            db.session.add(User("test1", "test1"))
        if not User.query.filter_by(username="test2").first():
            db.session.add(User("test2", "test2"))
        if not Role.query.filter_by(name="admin").first():
            db.session.add(Role("admin", "管理员"))
        db.session.commit()
        
        # Добавляем роль пользователю, если ещё не добавлена
        user = User.query.filter_by(username="test1").first()
        role = Role.query.filter_by(name="admin").first()
        if user and role and not user.has_role('admin'):
            user_datastore.add_role_to_user(user, role)
            db.session.commit()
except Exception as e:
    print(f"Error initializing database: {e}")
    db.session.rollback()