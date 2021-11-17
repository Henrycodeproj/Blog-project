from datetime import datetime
from enum import unique
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login.utils import login_required, login_user, logout_user
from flask.sessions import NullSession
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin, LoginManager
from sqlalchemy.orm import relation, relationship
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import ValidationError
from models import Addprofile, LoginForm, Register, Postform, Addprofile
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import datetime
import os
import secrets


app = Flask(__name__)
Bootstrap(app)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SECRET_KEY'] = "l6<E9kwpe0KyFWG$UP2&"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123123@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(UserMixin, db.Model): #user skeleton and columns for mysql database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique = False)
    username = db.Column(db.String(25), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(50), unique = True)
    profimage = db.Column(db.String(255))
    description = db.Column(db.Text)
    date_joined = db.Column(db.String(50))
    last_login = db.Column(db.String(50))
    posts = db.relationship('Posts', backref='poster', lazy = True)

class Posts(db.Model): #post skeleton and columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
    posting_user = db.Column(db.String(255))
    date_posted = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    words = db.Column(db.String(50))

def checkemail():
    user = Users.query.filter_by(email=request.form.get('email')).first()
    if user == None:
        return False
    else:
        return True

def checkusername():
    user = Users.query.filter_by(username = request.form.get('username')).first()
    if user == None:
        return False
    else:
        return True

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hex(file):
    random_hex = secrets.token_hex(10)
    split=os.path.splitext(file)
    return random_hex + split[1]

def word_check(data):
    word_set ={'penis','nigga','queer','fag','pussy','cunt','douche','nigger','retard','gay','chink'}
    if data in word_set:
        return True
    else:
        return False

@app.route('/test')
def test():
    old_image = current_user.profimage
    path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
    os.remove(path)
    current_user.profimage = None
    db.session.commit()
    return render_template('testing.html')

#homepage
@app.route ('/')
def index():
    posts = Posts.query.order_by(Posts.id.desc()).all()
    return render_template("homepage.html", posts = posts, loggedin = current_user.is_active, current_date = datetime.datetime.now().date())

# @app.route('/comments', methods = ["POST", "GET"])
# def comments():
#     form = Comments()
#     if request.method == "POST":
#         commenting = Comment(words = form.words.data)
#         db.session.add(commenting)
#         db.session.commit()
#     return render_template('test.html', form = form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_profile():
    profile = Addprofile()
    user = Users.query.get(current_user.id)
    if request.method == 'POST':  #allows user to add just description and passes onto to check other files
        if profile.description.data != '':
            user.description = profile.description.data
            db.session.add(user)
            db.session.commit()
            flash('You have sucessfully changed your profile description', 'prof_description')
            return redirect(url_for('dashboard'))
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if current_user.profimage == None:
                filename = secure_filename(file.filename)
                hexed_name = hex(filename) # passes original name of file and turns turns name into hex, prevents long names and overloads
                output_size = (300,300)
                picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
                picture.thumbnail(output_size, Image.ANTIALIAS)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
                user.profimage = hexed_name
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully uploaded a photo','prof_photo')
                return redirect(url_for('dashboard', name=filename))
            else:
                old_image = current_user.profimage # removes old photo from folder before updating
                path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
                os.remove(path)
                filename = secure_filename(file.filename)
                hexed_name = hex(filename) # passes original name of file and turns turns name into hex, prevents long names and overloads
                output_size = (300,300)
                picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
                picture.thumbnail(output_size, Image.ANTIALIAS)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
                user.profimage = hexed_name
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully uploaded a photo','prof_photo')
                return redirect(url_for('dashboard', name=filename))
    return render_template('upload.html', profile = profile)

#post editing
@app.route('/dashboard/edit/<postID>', methods = ["POST", "GET"])
def edit(postID):
    form = Postform()
    current_blog = Posts.query.get(postID)
    if current_user.username != current_blog.poster.username: #checks to make sure that user editing is the right user or else returns them to homepage
        flash('Error: You are not the original poster of this user', 'false_user')
        return redirect(url_for('index'))
    elif request.method == "POST":
        current_blog.title = form.title.data  #changes the actual post data
        current_blog.content = form.content.data
        db.session.add(current_blog)
        db.session.commit()
        flash('Your article has been successfully edited', 'edit')
        return redirect(url_for('index'))
    form.title.data = current_blog.title #fills in the form with title from id
    form.content.data = current_blog.content
    return render_template('post_edit.html', form = form)

#post deletion
@app.route('/delete/<postID>')
def delete(postID):
    try:
        delete_id = Posts.query.get(postID)
        old_image = delete_id.image # removes old photo from folder before updating
        path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
        os.remove(path)
        db.session.delete(delete_id)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        flash('Opps, something went wrong. Your post was not deleted')
        return redirect(url_for('delete'))

#posting for blog articles/status
@app.route('/dashboard/post', methods = ["POST", "GET"])
@login_required
def post():
    form = Postform()
    if request.method == "POST":
                #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hexed_name = hex(filename) # passes original name of file into hex function and returns hexed name, prevents long names, overloads, injections
            output_size = (300,300)
            picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
            picture.thumbnail(output_size, Image.ANTIALIAS)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
            posting = Posts(title = form.title.data, content = form.content.data, image = hexed_name, posting_user = current_user.username, date_posted = datetime.datetime.now().date(), poster_id = current_user.id)
            db.session.add(posting)
            db.session.commit()
            flash('Your post has been added', 'posted')
            return redirect(url_for('post'))
    else:
        return render_template("post.html", form = form, loggedin = current_user.is_active)

#dashboard for users,need working viewer count, article, customization
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("Dashboard.html", name = current_user.name, last_logged = current_user.last_login, profimage = current_user.profimage, description =current_user.description)

#login method
@app.route('/login', methods = ["POST", "GET"])
def login():
    form = LoginForm()
    if current_user.is_active == True:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) == True:
                login_user(user, remember = form.remember_me.data)
                flash('You have been successfully logged in!', 'success')
                return redirect(url_for('dashboard'))
        flash('Incorrect username or password', 'login_error')  
        return redirect(url_for('login'))
    return render_template("login.html", form = form)

@app.route('/password_reset')

#handles signup, checks database and returns messages
@app.route('/signup', methods = ["POST", "GET"])
def signup():
    form = Register()
    if form.validate_on_submit():
        if word_check(form.username.data) == True:
            flash('Your username contains an inappropriate word', 'inappropriate')
            return redirect(url_for('signup'))
        elif checkemail() and checkusername() == True:
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
            flash('You have succesfully created your account. You can now login.', 'creation')
            return redirect(url_for('login'))
    return render_template("signup.html", form = form)

#logout handler
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

