from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField, DateField, TextAreaField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User
from data.news import News
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    username = StringField('Никнейм', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    school = StringField('Школа', validators=[DataRequired()])
    class_number = StringField('Класс   ', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('СОЗДАТЬ АККАУНТ')

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    submit = SubmitField('Создать')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/main")
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        print(user)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        if user:
            print(f"Пользователь найден: {user.email}")
            print(f"Пароль из базы: {user.hashed_password}")
            print(f"Пароль из формы: {form.password.data}")

            if user.check_password(form.password.data):
                print("Пароль совпал! Логиним...")
                login_user(user, remember=form.remember_me.data)
                return redirect("/main")
            else:
                print("Ошибка: Пароль НЕ совпал.")
        else:
            print("Ошибка: Пользователь с такой почтой НЕ найден.")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/main")
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такая почта уже зарегистрирована")
        if form.password.data != form.password_confirm.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        user = User()
        user.surname = form.surname.data
        user.name = form.name.data
        user.patronymic = form.patronymic.data
        user.nickname = form.username.data
        user.email = form.email.data
        user.birthday = form.birthday.data
        user.school = form.school.data
        user.klass = form.class_number.data
        user.hashed_password = form.password.data
        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=True)
        return redirect("/main")
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/news')
@login_required
def news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).order_by(News.public_date.desc()).all()
    return render_template('news.html', news=news)

@app.route('/add_news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.author = current_user.nickname
        db_sess.add(news)
        db_sess.commit()
        return redirect('/news')
    return render_template('add_news.html', title='Создание новости', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Личный кабинет')

@app.route('/ege')
@login_required
def ege():
    return render_template('ege.html', title='ЕГЭ')

@app.route('/oge')
@login_required
def oge():
    return render_template('oge.html', title='ОГЭ')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    db_session.global_init("db/blogs.db")
    session = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
