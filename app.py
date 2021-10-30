from datetime import datetime
from enum import unique
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_login.utils import login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.fields.core import BooleanField
from wtforms.validators import ValidationError
from models import LoginForm, Register, Postform
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin, LoginManager
from flask_bootstrap import Bootstrap
import datetime


app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = "l6<E9kwpe0KyFWG$UP2&"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique = False)
    username = db.Column(db.String(25), unique = True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique = True)
    date_joined = db.Column(db.String(50))
    last_login = db.Column(db.String(50))

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)


def checkemail():
    user = Users.query.filter_by(email=request.form.get('email')).first()
    print(user)
    if user == None:
        return False
    else:
        return True

def checkusername():
    user = Users.query.filter_by(username = request.form.get('username')).first()
    print(user)
    if user == None:
        return False
    else:
        return True

@app.route ('/')
def index():
    return render_template("homepage.html")

@app.route('/dashboard/post', methods = ["POST", "GET"])
@login_required
def post():
    form = Postform()
    db.session.add(title = form.data.title, content = form.content.data)
    db.session.commit()
    return render_template("post.html", form = form)

@app.route('/login', methods = ["POST", "GET"])
def login():
    form = LoginForm()
    if current_user.is_active:
        return redirect(url_for('dashboard'))
    elif form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) == True:
                login_user(user, remember = form.remember_me.data)
                flash('You have been successfully logged in!', 'success')
                return redirect(url_for('dashboard'))
        flash('Incorrect username or password', 'login_error')  
        return redirect(url_for('login'))
    return render_template("login.html", form = form)

@app.route('/signup', methods = ["POST", "GET"])
def signup():
    form = Register()
    if form.validate_on_submit():
        if checkemail() and checkusername() == True:
            flash('Both Email and Username are taken!', 'email_username')
            return redirect(url_for("signup"))
        elif checkemail() == True:
            flash('Email is already taken', 'email')
            return redirect(url_for("signup"))
        elif checkusername() == True:
            flash('Username is already taken', 'username')
            return redirect(url_for("signup"))
        else:
            hashed_password=generate_password_hash(form.password.data, method = 'sha256')
            new_user = Users(name = form.name.data, username = form.username.data, password = hashed_password, email = form.email.data, date_joined = datetime.datetime.now())
            db.session.add(new_user)
            db.session.commit()
            flash('You have succesfully created your account. You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template("signup.html", form = form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("Dashboard.html", name = current_user.name, last_logged = current_user.last_login)

@app.route ('/logout')
@login_required
def logout():
    current_user.last_login = datetime.datetime.now().date()
    db.session.commit()
    logout_user()
    flash('You have been successfully logged out', 'logout')
    return redirect(url_for("login"))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

