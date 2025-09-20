__author__ = 'meha001'
from App import db
from flask_security import UserMixin, RoleMixin  # Исправленный импорт
from passlib.handlers.django import django_pbkdf2_sha256
from sqlalchemy.exc import NoResultFound, MultipleResultsFound


roles_users = db.Table('roles_users',  # 用户权限中间表
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):  # 权限表
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):  # 用户表
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username=None, password=None, active=True):
        self.username = username
        self.password = django_pbkdf2_sha256.encrypt(password)
        self.active = active  # Исправлено: используем переданный параметр

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def authenticate(cls, username, password):
        try:
            user = cls.query.filter(cls.username == username).one()
            if user and django_pbkdf2_sha256.verify(password, user.password):
                return user
            return None
        except NoResultFound:
            return None
        except MultipleResultsFound:
            # Логируем ошибку, если найдено несколько пользователей с одинаковым username
            print(f"Multiple users found with username: {username}")
            return None

    # Методы, требуемые Flask-Security
    def get_auth_token(self):
        # Нужно реализовать генерацию токена
        # Обычно это делается через itsdangerous или JWT
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)