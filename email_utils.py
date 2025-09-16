from itsdangerous import URLSafeTimedSerializer
from flask import url_for, render_template
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


def send_confirmation_email(user, app):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('email/confirm.html', confirm_url=confirm_url, user=user)
    subject = 'Подтвердите ваш email'
    msg = Message(subject=subject, recipients=[user.email], html=html, sender=app.config.get('MAIL_DEFAULT_SENDER'))
    mail.send(msg)