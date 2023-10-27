from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    """
    Form for user login.

    :param email: Email field for user login.
    :type email: StringField
    :param password: Password field for user login.
    :type password: PasswordField
    :param remember_me: Checkbox for remembering the user.
    :type remember_me: BooleanField
    :param submit: Submit button for form submission.
    :type submit: SubmitField
    """
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    """
    Form for user registration.

    :param login: Field for user's login name.
    :type login: StringField
    :param email: Email field for user registration.
    :type email: StringField
    :param password: Password field for user registration.
    :type password: PasswordField
    :param rep_password: Repeat password field for user registration.
    :type rep_password: PasswordField
    :param submit: Submit button for form submission.
    :type submit: SubmitField
    """
    login = StringField('Login', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rep_password = PasswordField('Repeat password',
                                 validators=[DataRequired(),
                                             EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign up')


class Search(FlaskForm):
    """
    Form for searching books.

    :param book_name: Field for entering the book name.
    :type book_name: StringField
    :param search: Submit button for form submission.
    :type search: SubmitField
    """
    book_name = StringField('Search books', description='Book search')
    search = SubmitField('Search')
