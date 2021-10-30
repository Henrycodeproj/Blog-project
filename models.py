from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,validators
from wtforms import widgets
from wtforms.validators import InputRequired, Email, Length
from wtforms.widgets import TextArea 


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 4, max = 25)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min = 6, max = 80)])
    remember_me = BooleanField('Remember me')

class Register(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min = 3, max = 30)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max = 50)])
    username = StringField('Username', validators=[InputRequired(), Length(min = 4, max = 30)])
    password = PasswordField('Password', validators=[InputRequired(), validators.EqualTo('confirm_password', message='Passwords must match'), Length(min = 6, max = 80)])
    confirm_password = PasswordField('Confirm Password')

class Postform(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min = 3, max = 50)])
    content = StringField('Content', validators=[InputRequired()], widget=TextArea())
    
