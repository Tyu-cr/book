import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager, logout_user, login_user, login_required, current_user
from requests import get

from app.db import db_session
from app.db.models.books import Books
from app.db.models.read_history import History
from app.db.models.user import User
from app.forms.forms import LoginForm, RegisterForm, Search

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
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    global GLOBAL_LOGIN
    logout_user()
    GLOBAL_LOGIN = None
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global GLOBAL_LOGIN
    login_form = LoginForm()
    form = RegisterForm()
    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception:
        GLOBAL_LOGIN = None
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    lst = []
    for i in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Sign up', form=form, login_form=login_form,
                                   message_reg='The passwords dont match')
        db_session.global_init('app/db/books.sqlite')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Sign up', form=form, login_form=login_form,
                                   message_reg='There is already such a user')
        user = User()
        user.login = form.login.data
        user.email = str(form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return render_template('library.html', title='Main page', form=form, login_form=login_form,
                               message='Registration was successful', lst=lst)
    if login_form.validate_on_submit():
        user = session.query(User).filter(User.email == login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('register')
        return render_template('library.html', title='Sign up',
                               message='Incorrect login or password', login_form=login_form, form=form)
    return render_template('register.html', title='Sign up', form=form, login_form=login_form)


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
    for i in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    if GLOBAL_LOGIN is None:
        if form.validate_on_submit():
            user = session.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                GLOBAL_LOGIN = user
                return redirect('/')
            return render_template('base_unreg.html', title='Main page',
                                   message='Incorrect login or password', login_form=form)
        return render_template('base_unreg.html', title='Main page', login_form=form)
    else:
        return render_template('library.html', title='Main page', login_form=form, lst=lst)


@app.route('/search', methods=['GET', 'POST'])
def search():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('search')
        return render_template('search.html', title='Search books',
                               message='Incorrect login or password', login_form=form, search_form=search_form)
    if search_form.validate_on_submit():
        if search_form.book_name.data == '':
            return render_template('search.html', title='Search books',
                                   login_form=form, search_form=search_form,
                                   message_search='Enter the title of the book or author')
        else:
            request = search_form.book_name.data
            books_json = get('https://www.googleapis.com/books/v1/volumes?q={}&key={}'.format(request, KEY)).json()
            GLOBAL_JSON = books_json
            GLOBAL_REQUEST = request
            return redirect('books_search')
    return render_template('search.html', title='Search books', login_form=form, search_form=search_form)


@app.route('/books_search', methods=['GET', 'POST'])
def books_search():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('books_search')
        return render_template('book_search.html', title='Search results',
                               message='Incorrect login or password',
                               login_form=form, json=GLOBAL_JSON, request=GLOBAL_REQUEST)
    return render_template('book_search.html', title='Search results', login_form=form,
                           json=GLOBAL_JSON, request=GLOBAL_REQUEST)


@app.route('/<request>/<id2>/', methods=['GET', 'POST'])
def add(request, id2):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('search.html', title='Search books',
                               message='Incorrect login or password', login_form=form, search_form=search_form)
    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Search books',
                               login_form=form, search_form=search_form,
                               message_search='You must be logged in to your account to add a book')
    books_json = get('https://www.googleapis.com/books/v1/volumes?q={}&key={}'.format
                     (request, KEY)).json()['items'][int(id2)]
    book = Books()
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
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
            return redirect('library')
        return render_template('library.html', title='Library', message='Incorrect login or password',
                               login_form=form)
    for i in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        lst.append([i.title, i.authors, i.date, i.image, i.description, i.language, i.count, i.href])
    return render_template('library.html', title='Library', login_form=form, lst=lst)


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
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('user.html', title='Users', message='Incorrect login or password',
                               login_form=form, global_login=int(GLOBAL_LOGIN))
    for i in session.query(User):
        a.append(i.id)
        a.append(i.login)
        a.append(i.email)
        a.append(i.modified_date)
        lst2.append(a)
        a = []
    if GLOBAL_LOGIN is not None:
        return render_template('user.html', title='Users', login_form=form, lst=lst2,
                               global_login=int(GLOBAL_LOGIN))
    else:
        return render_template('base_unreg.html', title='Main page', login_form=form)


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
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('history.html', title='History', message='Incorrect login or password',
                               login_form=form, lst=lst2)
    try:
        for i in session.query(History).filter(History.user_id == GLOBAL_LOGIN):
            a.append(i.title)
            a.append(i.authors)
            a.append(i.time)
            lst2.append(a)
            a = []
        return render_template('history.html', title='History', login_form=form, lst=lst2)
    except Exception:
        return render_template('history.html', title='History', login_form=form, lst=lst2)


@app.route('/add_hist/<title>/<authors>/<href>', methods=['GET', 'POST'])
def add_hist(title, authors, href):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init('app/db/books.sqlite')
    session = db_session.create_session()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            GLOBAL_LOGIN = user
        return render_template('search.html', title='Search books', message='Incorrect login or password',
                               login_form=form, search_form=search_form)
    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Search books', login_form=form, search_form=search_form)
    hist = History()
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
