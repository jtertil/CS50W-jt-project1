from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,\
    SelectField
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


class ReviewForm(FlaskForm):
    review = TextAreaField('search', validators=[Length(3, 300)])
    rating = SelectField(
        'ratings',
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    submit = SubmitField('submit')
