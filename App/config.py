__author__ = 'meha001'

# Flask
DEBUG = True  # Для продакшена установите False!
FLASK_ENV = 'development'  # Добавьте для ясности

# Database
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/database_name'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Измените на False для производительности
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 280,
    'pool_pre_ping': True,
}

# Flask-Security
SECRET_KEY = 'my_secret_key'  # ЗАМЕНИТЕ на случайный надежный ключ!
SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'  # Добавьте для ясности
SECURITY_TOKEN_AUTHENTICATION_REALM = 'Authentication Required'
WTF_CSRF_ENABLED = False  # Для API обычно отключают
SECURITY_TOKEN_MAX_AGE = 86400  # 24 часа
SECURITY_UNAUTHORIZED_VIEW = '/'

# Дополнительные рекомендуемые настройки
SECURITY_PASSWORD_HASH = 'django_pbkdf2_sha256'  # Соответствует вашему коду
SECURITY_PASSWORD_SALT = 'your_password_salt_here'  # Добавьте для безопасности
SECURITY_TRACKABLE = True  # Отслеживание логинов
SECURITY_RECOVERABLE = True  # Восстановление пароля
SECURITY_CHANGEABLE = True  # Смена пароля

# Настройки для REST API
SECURITY_RETURN_GENERIC_RESPONSES = True  # Для API лучше True
SECURITY_CSRF_PROTECT_MECHANISMS = ['session']  # Для API обычно не нужно
SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True