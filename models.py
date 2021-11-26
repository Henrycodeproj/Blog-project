from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,PasswordField,BooleanField,validators
from wtforms import widgets
from wtforms.fields.simple import FileField
from wtforms.validators import InputRequired, Email, Length
from wtforms.widgets import TextArea
from wtforms.widgets.core import Input 


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min = 6, max = 80)])
    remember_me = BooleanField('Remember me')

class Register(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min = 3, max = 30)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max = 50)])
    username = StringField('Username', validators=[InputRequired(), Length(min = 3, max = 30)])
    password = PasswordField('Password', validators=[InputRequired(), validators.EqualTo('confirm_password', message='Passwords must match'), Length(min = 6, max = 80)])
    confirm_password = PasswordField('Confirm Password')

class Postform(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min = 3, max = 50)])
    content = StringField('Content', validators=[InputRequired()], widget=TextArea())
    file = FileField('image', validators=[FileAllowed(['jpg', 'png'])])
    
class Addprofile(FlaskForm):
    file = FileField('image', validators=[FileAllowed(['jpg', 'png'])])
    description = StringField('Description', validators=[Length(min=0, max = 255)], widget=TextArea())

class Passwordrequest(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max = 50)])

class Passwordsuccess(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), validators.EqualTo('confirm_password', message='Passwords must match'), Length(min = 6, max = 80)])
    confirm_password = PasswordField('Confirm Password')

class Commentsform(FlaskForm):
    comment = StringField('comment', validators=[InputRequired()], widget=TextArea())