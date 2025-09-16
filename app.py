from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from extensions import db, mail, login_manager
from models import User
from forms import RegistrationForm, LoginForm
from email_utils import send_confirmation_email, confirm_token
from flask_login import login_user, logout_user, login_required, current_user


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(email=form.email.data.lower(), username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            # send confirmation
            try:
                send_confirmation_email(user, app)
                flash('Регистрация успешна. Проверьте почту и подтвердите аккаунт.', 'success')
            except Exception as e:
                # на проде логируй ошибку
                flash('Не удалось отправить письмо. Обратитесь к администратору.', 'warning')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/confirm/<token>')
    def confirm_email(token):
        email = confirm_token(token)
        if not email:
            flash('Ссылка недействительна или устарела.', 'danger')
            return redirect(url_for('index'))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Пользователь не найден.', 'warning')
            return redirect(url_for('index'))
        if user.confirmed:
            flash('Уже подтверждено. Войдите.', 'info')
            return redirect(url_for('login'))
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Email подтверждён. Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and user.check_password(form.password.data):
                if not user.confirmed:
                    flash('Подтвердите email прежде чем входить.', 'warning')
                    return redirect(url_for('unconfirmed'))
                login_user(user)
                flash('Вы вошли в систему.', 'success')
                return redirect(url_for('dashboard'))
            flash('Неправильный email или пароль.', 'danger')
        return render_template('login.html', form=form)

    @app.route('/unconfirmed')
    def unconfirmed():
        return render_template('unconfirmed.html')

    @app.route('/resend')
    def resend_confirmation():
        if not current_user.is_authenticated:
            flash('Сначала войдите, чтобы отправить письмо повторно.', 'info')
            return redirect(url_for('login'))
        if current_user.confirmed:
            flash('Уже подтвержден.', 'info')
            return redirect(url_for('dashboard'))
        try:
            send_confirmation_email(current_user, app)
            flash('Письмо отправлено повторно.', 'success')
        except Exception:
            flash('Не удалось отправить письмо.', 'danger')
        return redirect(url_for('unconfirmed'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Вы вышли.', 'info')
        return redirect(url_for('index'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)