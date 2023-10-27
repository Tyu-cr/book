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
DB_SESSION = 'app/db/books.sqlite'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main():
    global GLOBAL_LOGIN
    login_form = LoginForm()
    # TODO: move to config
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()
    book_lst = []

    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception as e:
        print(e)
        GLOBAL_LOGIN = None

    for book in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        book_lst.append([book.title, book.authors, book.date, book.image,
                         book.description, book.language, book.count, book.href])

    if GLOBAL_LOGIN is None:
        if login_form.validate_on_submit():
            user_session = session.query(User).filter(User.email == login_form.email.data).first()

            if user_session and user_session.check_password(login_form.password.data):
                login_user(user_session, remember=login_form.remember_me.data)
                GLOBAL_LOGIN = user_session
                return redirect('/')

            return render_template('base_unreg.html', title='Main page',
                                   message='Incorrect login or password', login_form=login_form)

        return render_template('base_unreg.html', title='Main page', login_form=login_form)

    else:
        return render_template('library.html', title='Main page',
                               login_form=login_form, lst=book_lst)


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
    except Exception as e:
        print(e)
        GLOBAL_LOGIN = None

    db_session.global_init(DB_SESSION)
    session = db_session.create_session()
    book_lst = []

    for book in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        book_lst.append([book.title, book.authors, book.date, book.image,
                         book.description, book.language, book.count, book.href])

    if form.validate_on_submit():
        if form.password.data != form.rep_password.data:
            return render_template('register.html', title='Sign up', form=form,
                                   login_form=login_form, message_reg='The passwords dont match')

        db_session.global_init(DB_SESSION)
        session = db_session.create_session()

        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Sign up', form=form,
                                   login_form=login_form, message_reg='There is already such a user')

        user_session = User()
        user_session.login = form.login.data
        user_session.email = str(form.email.data)
        user_session.set_password(form.password.data)
        session.add(user_session)
        session.commit()

        return render_template('library.html', title='Main page', form=form,
                               login_form=login_form, message='Registration was successful', lst=book_lst)

    if login_form.validate_on_submit():
        user_session = session.query(User).filter(User.email == login_form.email.data).first()

        if user_session and user_session.check_password(login_form.password.data):
            login_user(user_session, remember=login_form.remember_me.data)
            GLOBAL_LOGIN = user_session
            return redirect('register')

        return render_template('library.html', title='Sign up',
                               message='Incorrect login or password', login_form=login_form, form=form)

    return render_template('register.html', title='Sign up', form=form, login_form=login_form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()

        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
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
            books_json = get(f'https://www.googleapis.com/books/v1/volumes?q={request}&key={KEY}').json()
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
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()

        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
            return redirect('books_search')

        return render_template('book_search.html', title='Search results',
                               message='Incorrect login or password', login_form=form,
                               json=GLOBAL_JSON, request=GLOBAL_REQUEST)

    return render_template('book_search.html', title='Search results', login_form=form,
                           json=GLOBAL_JSON, request=GLOBAL_REQUEST)


@app.route('/<request>/<id2>/', methods=['GET', 'POST'])
def add(request, id2):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()

        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
        return render_template('search.html', title='Search books',
                               message='Incorrect login or password', login_form=form, search_form=search_form)

    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Search books',
                               login_form=form, search_form=search_form,
                               message_search='You must be logged in to your account to add a book')

    books_json = get(f'https://www.googleapis.com/books/v1/volumes?q={request}&key={KEY}').json()['items'][int(id2)]
    book = Books()
    book.user_id = GLOBAL_LOGIN
    book.title = books_json['volumeInfo'].get('title')
    book.authors = ', '.join(books_json['volumeInfo'].get('authors', []))
    book.date = books_json['volumeInfo'].get('publishedDate')
    book.image = books_json['volumeInfo']['imageLinks'].get('thumbnail')
    book.description = books_json['volumeInfo'].get('description')
    book.language = books_json['volumeInfo'].get('language')
    book.count = books_json['volumeInfo'].get('pageCount')
    book.href = books_json['volumeInfo'].get('previewLink')
    session.add(book)
    session.commit()
    return redirect('/')


@app.route('/library', methods=['GET', 'POST'])
def library():
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    book_lst = []
    form = LoginForm()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()

        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
            return redirect('library')

        return render_template('library.html', title='Library', message='Incorrect login or password',
                               login_form=form)

    for book in session.query(Books).filter(Books.user_id == GLOBAL_LOGIN):
        book_lst.append([book.title, book.authors, book.date, book.image,
                         book.description, book.language, book.count, book.href])

    return render_template('library.html', title='Library', login_form=form, lst=book_lst)


@app.route('/user', methods=['GET', 'POST'])
def user():
    global GLOBAL_LOGIN

    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception as e:
        print(e)
        GLOBAL_LOGIN = None

    book_lst = []
    form = LoginForm()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()
        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
        return render_template('user.html', title='Users', message='Incorrect login or password',
                               login_form=form, global_login=int(GLOBAL_LOGIN))

    for user_i in session.query(User):
        book_lst.append([user_i.id, user_i.login, user_i.email, user_i.modified_date])

    if GLOBAL_LOGIN is not None:
        return render_template('user.html', title='Users', login_form=form, lst=book_lst,
                               global_login=int(GLOBAL_LOGIN))
    else:
        return render_template('base_unreg.html', title='Main page', login_form=form)


@app.route('/history', methods=['GET', 'POST'])
def history():
    global GLOBAL_LOGIN

    try:
        GLOBAL_LOGIN = current_user.get_id()
    except Exception as e:
        print(e)
        GLOBAL_LOGIN = None

    book_lst = []
    form = LoginForm()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()
        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
        return render_template('history.html',
                               title='History', message='Incorrect login or password', login_form=form, lst=book_lst)
    try:
        for history_i in session.query(History).filter(History.user_id == GLOBAL_LOGIN):
            book_lst.append([history_i.title, history_i.authors, history_i.time])
        return render_template('history.html', title='History', login_form=form, lst=book_lst)

    except Exception as e:
        print(e)
        return render_template('history.html', title='History', login_form=form, lst=book_lst)


@app.route('/add_hist/<title>/<authors>/<href>', methods=['GET', 'POST'])
def add_hist(title, authors, href):
    global GLOBAL_JSON
    global GLOBAL_REQUEST
    global GLOBAL_LOGIN
    form = LoginForm()
    search_form = Search()
    db_session.global_init(DB_SESSION)
    session = db_session.create_session()

    if form.validate_on_submit():
        user_session = session.query(User).filter(User.email == form.email.data).first()

        if user_session and user_session.check_password(form.password.data):
            login_user(user_session, remember=form.remember_me.data)
            GLOBAL_LOGIN = user_session
        return render_template('search.html', title='Search books', message='Incorrect login or password',
                               login_form=form, search_form=search_form)

    if GLOBAL_LOGIN is None:
        return render_template('search.html', title='Search books',
                               login_form=form, search_form=search_form)

    hist = History()
    hist.user_id = GLOBAL_LOGIN
    hist.title = title

    try:
        hist.authors = authors
    except Exception as e:
        print(e)
        hist.authors = None

    hist.time = datetime.datetime.now()
    session.add(hist)
    session.commit()
    return redirect(f'http://books.google.ru/books?{href}')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
