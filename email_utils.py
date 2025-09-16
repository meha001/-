from itsdangerous import URLSafeTimedSerializer
from flask import url_for, render_template, current_app
from config import Config
from extensions import mail
from flask_mail import Message

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def generate_confirmation_token(email: str) -> str:
    return serializer.dumps(email, salt=Config.CONFIRM_SALT)

def confirm_token(token: str, expiration: int = None):
    expiration = expiration or Config.CONFIRM_TOKEN_EXP
    try:
        email = serializer.loads(token, salt=Config.CONFIRM_SALT, max_age=expiration)
    except Exception:
        return None
    return email

def send_confirmation_email(user):
    # Используем current_app вместо передачи app в аргументах
    with current_app.app_context():  # Создаем контекст приложения
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/confirm.html', confirm_url=confirm_url, user=user)
        subject = 'Подтвердите ваш email'
        
        # Получаем отправителя из конфигурации
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        msg = Message(
            subject=subject, 
            recipients=[user.email], 
            html=html, 
            sender=sender
        )
        
        mail.send(msg)