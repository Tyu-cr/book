from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField
from wtforms.validators import DataRequired


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
