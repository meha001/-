from flask import Flask, render_template, redirect, url_for, flash, session, request
from config import Config
from extensions import db, mail
from models import User
from forms import RegistrationForm, LoginForm
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from functools import wraps

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def send_email(to, subject, body, app):
    # Всегда отправляем реальные письма
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        print(f"✅ Email отправлен на: {to}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        flash('Ошибка отправки email. Попробуйте позже.', 'danger')
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите для доступа к этой странице.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all() 
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            existing_user = User.query.filter((User.email == form.email.data) | 
                                            (User.username == form.username.data)).first()
            if existing_user:
                flash('Пользователь с таким email или именем уже существует.', 'danger')
                return render_template('register.html', form=form)
                
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            token = serializer.dumps(user.email, salt='email-confirm')
            confirm_url = url_for('confirm_email', token=token, _external=True)
            
            send_email(user.email, 'Сайт Шаурма в Пите🥙', 
                      f'Нажми на ссылку чтобы подтвердить email, Быстро очень Быстро !!!: {confirm_url}', app)

            flash('Регистрация успешна. Проверьте почту для подтверждения email.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                # В режиме разработки пропускаем проверку подтверждения
                if not app.config.get('DEBUG', True) and not user.confirmed:
                    flash('Подтвердите ваш email перед входом.', 'warning')
                    return render_template('login.html', form=form)
                    
                session.clear()
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Вы успешно вошли.', 'success')
                return redirect(url_for('dashboard'))
            flash('Неверный email или пароль.', 'danger')
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Вы вышли из системы.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', username=session.get('username'))

    @app.route('/confirm/<token>')
    def confirm_email(token):
        try:
            email = serializer.loads(token, salt='email-confirm', max_age=3600)
        except:
            flash('Ссылка недействительна или истекла.', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash('Email уже подтвержден.', 'info')
        else:
            user.confirmed = True
            db.session.commit()
            flash('Email подтвержден! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    @app.route('/test-confirm/<email>')
    def test_confirm(email):
        """Маршрут для тестирования подтверждения без email"""
        if not app.config.get('DEBUG', True):
            flash('Доступно только в режиме разработки', 'danger')
            return redirect(url_for('index'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            user.confirmed = True
            db.session.commit()
            flash(f'Email {email} подтвержден для тестирования', 'success')
        else:
            flash('Пользователь не найден', 'danger')
        return redirect(url_for('login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)