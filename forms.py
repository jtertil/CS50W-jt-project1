from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo


class LoginForm(FlaskForm):
    login = StringField('login', validators=[InputRequired(), Length(3, 64)])
    passw = PasswordField('password', validators=[InputRequired()])
    submit = SubmitField('login')


class RegisterForm(FlaskForm):
    login = StringField(
        'login',
        validators=[InputRequired(), Length(3, 64)])
    passw = PasswordField(
        'password',
        validators=[InputRequired(), Length(3, 64)])
    passw_c = PasswordField(
        'password confirmation',
        validators=[InputRequired(),
                    EqualTo('passw', message='Password must match.')])
    submit = SubmitField('register')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[InputRequired(), Length(3, 64)])
    submit = SubmitField('submit')
