import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager, logout_user, login_user, login_required, current_user
from flask_wtf import FlaskForm
from requests import get
from wtforms import PasswordField, SubmitField, BooleanField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from app.db import db_session
from app.db.models import users, read_history, books

# TODO: add to config
KEY = 'AIzaSyDBAFxQBMQ1Kovq62NpmGhW0mIuJSP0hH4'
GLOBAL_JSON = None
GLOBAL_REQUEST = None
GLOBAL_LOGIN = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(users.User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    global GLOBAL_LOGIN
    logout_user()
    GLOBAL_LOGIN = None
    return redirect('/')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    rep_password = PasswordField('Повтор пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистироваться')


class Search(FlaskForm):
    book_name = StringField('Поиск книг', description='Поиск книг')
    search = SubmitField('Искать')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global GLOBAL_LOGIN
    login_form = LoginForm()
    form = RegisterForm()
    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception:
        GLOBAL_LOGIN = None
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    lst = []
    for i in session.query(books.Books).filter(books.Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Регистрация', form=form, login_form=login_form,
                                   message_reg='Пароли не совпадают')
        db_session.global_init('db/books.sqlite')
        session = db_session.create_session()
        if session.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, login_form=login_form,
                                   message_reg='Такой пользователь уже есть')
        user = users.User()
        user.login = form.login.data
        user.email = str(form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return render_template('library.html', title='Главная', form=form, login_form=login_form,
                               message='Регистрация прошла успешно', lst=lst)
    if login_form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('register')
        return render_template('library.html', title='Регистрация', message='Неправильный логин или пароль',
                               login_form=login_form, form=form)
    return render_template('register.html', title='Регистрация', form=form, login_form=login_form)


@app.route('/', methods=['GET', 'POST'])
def main():
    global GLOBAL_LOGIN
    form = LoginForm()
    # TODO: move to config
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    lst = []
    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception:
        GLOBAL_LOGIN = None
    for i in session.query(books.Books).filter(books.Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    if GLOBAL_LOGIN is None:
        if form.validate_on_submit():
            user = session.query(users.User).filter(users.User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                GLOBAL_LOGIN = user
                return redirect('/')
            return render_template('base_unreg.html', title='Главная', message='Неправильный логин или пароль',
                                   login_form=form)
        return render_template('base_unreg.html', title='Главная', login_form=form)
    else:
        return render_template('library.html', title='Главная', login_form=form, lst=lst)


@app.route('/search', methods=['GET', 'POST'])
def search():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('search')
        return render_template('search.html', title='Поиск книг', message='Неправильный логин или пароль',
                               login_form=form, search_form=search_form)
    if search_form.validate_on_submit():
        if search_form.book_name.data == '':
            return render_template('search.html', title='Поиск книг', login_form=form, search_form=search_form,
                                   message_search='Введите название книги или автора')
        else:
            request = search_form.book_name.data
            books_json = get('https://www.googleapis.com/books/v1/volumes?q={}&key={}'.format(request, KEY)).json()
            GLOBAL_JSON = books_json
            GLOBAL_REQUEST = request
            return redirect('books_search')
    return render_template('search.html', title='Поиск книг', login_form=form, search_form=search_form)


@app.route('/books_search', methods=['GET', 'POST'])
def books_search():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('books_search')
        return render_template('book_search.html', title='Результаты поиска', message='Неправильный логин или пароль',
                               login_form=form, json=GLOBAL_JSON, request=GLOBAL_REQUEST)
    return render_template('book_search.html', title='Результаты поиска', login_form=form, json=GLOBAL_JSON,
                           request=GLOBAL_REQUEST)


@app.route('/<request>/<id2>/', methods=['GET', 'POST'])
def add(request, id2):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('search.html', title='Поиск книг', message='Неправильный логин или пароль',
                               login_form=form, search_form=search_form)
    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Поиск книг', login_form=form, search_form=search_form,
                               message_search='Для добавления книги нужно войти в аккаунт')
    books_json = get('https://www.googleapis.com/books/v1/volumes?q={}&key={}'.format
                     (request, KEY)).json()['items'][int(id2)]
    book = books.Books()
    book.user_id = GLOBAL_LOGIN
    book.title = books_json['volumeInfo']['title']
    try:
        book.authors = ', '.join(books_json['volumeInfo']['authors'])
    except Exception:
        book.authors = None
    try:
        book.date = books_json['volumeInfo']['publishedDate']
    except Exception:
        book.date = None
    try:
        book.image = books_json['volumeInfo']['imageLinks']['thumbnail']
    except Exception:
        book.image = None
    try:
        book.description = books_json['volumeInfo']['description']
    except Exception:
        book.description = None
    try:
        book.language = books_json['volumeInfo']['language']
    except Exception:
        book.language = None
    try:
        book.count = books_json['volumeInfo']['pageCount']
    except Exception:
        book.count = None
    book.href = books_json['volumeInfo']['previewLink']
    session.add(book)
    session.commit()
    return redirect('/')


@app.route('/library', methods=['GET', 'POST'])
def library():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    lst = []
    form = LoginForm()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('library')
        return render_template('library.html', title='Библиотека', message='Неправильный логин или пароль',
                               login_form=form)
    for i in session.query(books.Books).filter(books.Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    return render_template('library.html', title='Библиотека', login_form=form, lst=lst)


@app.route('/user', methods=['GET', 'POST'])
def user():
    global GLOBAL_LOGIN
    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception:
        GLOBAL_LOGIN = None
    a = []
    lst2 = []
    form = LoginForm()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('user.html', title='Пользователи', message='Неправильный логин или пароль',
                               login_form=form, global_login=int(GLOBAL_LOGIN))
    for i in session.query(users.User):
        a.append(i.id)
        a.append(i.login)
        a.append(i.email)
        a.append(i.modified_date)
        lst2.append(a)
        a = []
    if GLOBAL_LOGIN is not None:
        return render_template('user.html', title='Пользователи', login_form=form, lst=lst2,
                               global_login=int(GLOBAL_LOGIN))
    else:
        return render_template('base_unreg.html', title='Главная', login_form=form)


@app.route('/history', methods=['GET', 'POST'])
def history():
    global GLOBAL_LOGIN
    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception:
        GLOBAL_LOGIN = None
    a = []
    lst2 = []
    form = LoginForm()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('history.html', title='История', message='Неправильный логин или пароль',
                               login_form=form, lst=lst2)
    try:
        for i in session.query(read_history.History).filter(read_history.History.user_id == GLOBAL_LOGIN):
            a.append(i.title)
            a.append(i.authors)
            a.append(i.time)
            lst2.append(a)
            a = []
        return render_template('history.html', title='История', login_form=form, lst=lst2)
    except Exception:
        return render_template('history.html', title='История', login_form=form, lst=lst2)


@app.route('/add_hist/<title>/<authors>/<href>', methods=['GET', 'POST'])
def add_hist(title, authors, href):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(users.User).filter(users.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('search.html', title='Поиск книг', message='Неправильный логин или пароль',
                               login_form=form, search_form=search_form)
    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Поиск книг', login_form=form, search_form=search_form)
    hist = read_history.History()
    hist.user_id = GLOBAL_LOGIN
    hist.title = title
    try:
        hist.authors = authors
    except Exception:
        hist.authors = None
    hist.time = datetime.datetime.now()
    session.add(hist)
    session.commit()
    return redirect('http://books.google.ru/books?{}'.format(href))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
