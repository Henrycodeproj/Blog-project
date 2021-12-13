from datetime import datetime
from enum import unique
from flask_login.mixins import AnonymousUserMixin
from flask import Flask, json, render_template, request, url_for, redirect, flash, jsonify
from flask_login.utils import login_required, login_user, logout_user
from flask.sessions import NullSession
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import Pagination, SQLAlchemy
from flask_login import current_user, UserMixin, LoginManager
from itsdangerous.serializer import Serializer
from sqlalchemy.orm import dynamic_loader, relation, relationship
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import ValidationError
from models import Addprofile, LoginForm, Register, Postform, Addprofile, Passwordrequest, Passwordsuccess, Commentsform
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
#from sqlalchemy import func
from sqlalchemy.sql.expression import func
import random
import datetime
import os
import secrets


app = Flask(__name__)
Bootstrap(app)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'lihenryhl.work@gmail.com'
app.config['MAIL_PASSWORD'] = 'Creation101'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

likes = db.Table('likes',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
)

followers = db.Table('followers',
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
)

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
    profile_views = db.Column(db.Integer)
    total_post = db.Column(db.Integer)
    posts = db.relationship('Posts', backref='poster', lazy = True)
    comments = db.relationship('Comments', backref='commentor', lazy = True)
    likes = db.relationship('Posts', secondary=likes, lazy='subquery',
        backref=db.backref('liking', lazy=True))
    followers = db.relationship(
                             'Users',
                             secondary=followers,
                             primaryjoin=(followers.c.followed_id == id),
                             secondaryjoin=(followers.c.follower_id == id),
                             backref = db.backref('follows', lazy=True), lazy=True,
                             )


class Posts(db.Model): #post skeleton and columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    image = db.Column(db.String(255))
    posting_user = db.Column(db.String(255))
    date_posted = db.Column(db.String(255))
    article_views = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comments', backref = 'user_comments', lazy = True)
    genres = db.relationship('Categories', backref='genre', lazy=True)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posting_user = db.Column(db.String(255))
    comment = db.Column(db.Text)
    date = db.Column(db.String(255))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

@app.route('/followers/<posting_user>', methods = ["GET","POST"])
def followers(posting_user):
    random_user = Users.query.get(posting_user)
    random_user.follows.append(current_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/jscript', methods = ["GET"])
def script():
    likes=Posts.query.filter_by(id = 1).first()
    test = {'likes':likes.id}
    jsonify(test)
    return render_template('test.html', test=test)

@app.route('/likes/<post_id>', methods = ["GET", "POST"])
def likes(post_id):
    if request.method == "GET":
        current_posting =Posts.query.filter_by(id=post_id).first()
        current_posting.liking.append(current_user)
        db.session.commit()
        return redirect(url_for('expanded_post', postID = post_id))
    




'''@app.route('/test') #How I will add tags, finally 
def test():
    adventure=Adventure(title = "test2")
    rpg=Rpg(title = "test2")
    db.session.add(rpg)
    db.session.add(adventure)
    db.session.commit()
    cate_id= Adventure.query.filter_by(title = "test2").first()
    category_id=Rpg.query.filter_by(title = "test").first()
    category_id.category.append(cate_id)
    db.session.commit()
    fun=Rpg.query.filter_by(title = 'test').first()
    return render_template('test.html', fun = fun)'''

def testing(category):
    return str(category)

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

def word_check(word_data):
    word_set ={'penis','nigga','queer','fag','pussy','cunt','douche','nigger','retard','gay','chink'}
    if word_data in word_set:
        return True
    else:
        return False

def get_reset_token(user):
    serial = Serializer(app.config['SECRET_KEY'], expires_in=900) # 15 mins in seconds
    return serial.dumps({'user_id':user.id}).decode('utf-8')

def verify_token(token):
    serial = Serializer(app.config['SECRET_KEY'])
    print(serial)
    try:
        user_id = serial.loads(token)['user_id']
    except:
        return None
    return Users.query.get(user_id)

def send_mail(user):
    token = get_reset_token(user)
    print(token)
    message = Message('Password Reset Request', recipients = [user.email], sender='noreply@gmail.com')
    message.body= f'''
To Reset your password, click the following link:
{url_for('reset_token', token = token, _external = True)}
If you did not send this email, please ignore this message.
'''
    mail.send(message)

#homepage
@app.route ('/')
def index():
    hottest_post=db.session.query(func.max(Posts.article_views)).scalar()
    hottest_post_id=Posts.query.filter_by(article_views = hottest_post).first()
    page = request.args.get('page', 1, type = int)
    posts = Posts.query.order_by(Posts.id.desc()).paginate(page = page, per_page = 3)
    newest_user = Users.query.order_by(Users.id.desc()).all()
    random_users=Users.query.order_by(Users.id).all()
    random.shuffle(random_users) # shuffles list of users and will return first 3 -> (random_list[0:3])
    random_users_list = []
    for users in random_users: #printing users max views, still need to get ids and link to the post.
        max_views = db.session.query(func.max(Posts.article_views)).filter_by(posting_user = users.username).scalar()
        top_post_id=Posts.query.filter_by(article_views = max_views, posting_user = users.username).first()
        if len(random_users_list) < 3:
            if top_post_id is not None:
                random_users_list.append(top_post_id)
        else:
            break
    return render_template("homepage.html", posts = posts, loggedin = current_user.is_active, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, random_users_list = random_users_list)

@app.route ('/user/<username>')
def all_post(username):
    hottest_post=db.session.query(func.max(Posts.article_views)).scalar()
    hottest_post_id=Posts.query.filter_by(article_views = hottest_post).first()
    page = request.args.get('page', 1, type = int)
    user = Users.query.filter_by(username = username).first_or_404()
    posts = Posts.query.filter_by(posting_user=user.username).order_by(Posts.id.desc()).paginate(page = page, per_page = 3)
    newest_user = Users.query.order_by(Users.id.desc()).all()
    newest_posts = Posts.query.order_by(Posts.id.desc()).first()
    print(posts.items)
    if posts.items == []:
        flash('You do not have any current post to show!', 'no_post')
        return redirect(url_for('dashboard'))
    return render_template("total_users_post.html", posts = posts, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, user = user, loggedin = current_user.is_active, newest_posts = newest_posts)

@app.route ('/tag/<category>')
def categories(category):
    hottest_post=db.session.query(func.max(Posts.article_views)).scalar()
    hottest_post_id=Posts.query.filter_by(article_views = hottest_post).first()
    page = request.args.get('page', 1, type = int)
    posts = Categories.query.filter_by(category = category).order_by(Categories.id.desc()).paginate(page = page, per_page = 3)
    newest_user = Users.query.order_by(Users.id.desc()).all()
    newest_posts = Posts.query.order_by(Posts.id.desc()).first()
    if posts.items == []:
        flash('There are currently no post in that category.', 'no_post')
        return redirect(url_for('index'))
    return render_template("category_tag.html", posts = posts, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, loggedin = current_user.is_active, newest_posts = newest_posts, category = category)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_profile():
    profile = Addprofile()
    user = Users.query.get(current_user.id)
    if request.method == 'POST':  #allows user to add just description and passes onto to file check for further submission
        if profile.description.data != '':
            user.description = profile.description.data
            db.session.add(user)
            db.session.commit()
            flash('You have sucessfully changed your profile description!', 'prof_description')
            return redirect(url_for('dashboard'))
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('There was not file uploaded!', 'no_file')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file','no_name')
            # return redirect(request.url)
            return redirect(url_for('dashboard'))
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
                flash('You have sucessfully uploaded your profile picture.','prof_photo')
                return redirect(url_for('dashboard', name=filename))
            else:
                old_image = current_user.profimage # removes old photo from folder before updating current photo
                path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
                os.remove(path)
                filename = secure_filename(file.filename)
                hexed_name = hex(filename) # passes original name of file and turns turns name into hex, prevents long names and overloads
                output_size = (300,300)
                picture = Image.open(file) # converts uploaded images into smaller thumbnails or any pixel related size
                picture.thumbnail(output_size, Image.ANTIALIAS)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
                user.profimage = hexed_name
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully changed your profile photo','prof_photo')
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
    poster = Posts.query.get(postID)
    if current_user.username != poster.posting_user:
        flash('You can only delete your own post.', 'false_user')
        return redirect(url_for('index'))
    try:
        delete_id = Posts.query.get(postID)
        category_id = Categories.query.filter_by(post_id = delete_id.id).first()
        #category_id = Categories.filter_by()
        old_image = delete_id.image # removes old photo from folder before updating
        path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
        os.remove(path)
        current_user.total_post -= 1
        db.session.delete(delete_id)
        db.session.delete(category_id)
        db.session.commit()
        flash('Your post has been sucessfully deleted', 'success')
        return redirect(url_for('index'))
    except:
        flash('Opps, something went wrong. Your post was not deleted.', 'false_user')
        return redirect(url_for('index'))

@app.route('/view/<postID>', methods = ["POST", "GET"])
def expanded_post(postID):
    show_comments = Comments.query.filter_by(post_id = postID).all() #gets all post that equals the to current post
    original_poster = Posts.query.get(postID)
    expanded_post=Posts.query.get(postID)
    number_of_likes = expanded_post.liking
    print(number_of_likes)
    form = Commentsform()
    print(current_user)
    if current_user.get_id() == None or current_user.username != original_poster.posting_user:
        expanded_post.article_views += 1
        db.session.commit()
    if request.method == "POST":
        comment = Comments(comment=form.comment.data, post_id = postID, date = datetime.datetime.now().date(), posting_user = current_user.username, poster_id = current_user.id)
        print(current_user.profimage)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('expanded_post', postID = postID))
        #poster_image = current_user.profimage
    return render_template('expanded_post.html', expanded_post = expanded_post, form = form, show_comments = show_comments, loggedin = current_user.is_active, current_user_check = current_user.is_anonymous, current_user = current_user, likes = len(number_of_likes)) # current_user doesn't work if changed to check if user is active. So i passed two variables instead to check for if the user exist and then the method to call image

#posting for blog articles/status
@app.route('/post', methods = ["POST", "GET"])
@login_required
def post():
    form = Postform()
    if request.method == "POST":
        #check if the post request has the file
        if 'file' not in request.files:
            print('No file part')
            return redirect(url_for('post'))
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hexed_name = hex(filename) # passes original name of file into hex function and returns hexed name, prevents long names, overloads, injections
            output_size = (550,550)
            picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
            picture.thumbnail(output_size, Image.ANTIALIAS)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
            posting = Posts(title = form.title.data, content = form.content.data, image = hexed_name, posting_user = current_user.username, date_posted = datetime.datetime.now().date(), article_views = 0, poster_id = current_user.id, likes = 0, dislikes = 0)
            current_user.total_post += 1
            db.session.add(posting)
            db.session.commit()
            postid = Posts.query.filter_by(title = form.title.data, posting_user = current_user.username).first()
            category= Categories(category = request.form['genre'], post_id = postid.id)
            db.session.add(category)
            db.session.commit()
            #new_post_id = Posts.query.filter_by(image = hexed_name, posting_user = current_user.username).first()
            #new_post_id.liking.append(current_user)
            db.session.commit()
            flash('Your post has been added', 'posted')
            return redirect(url_for('post'))
    else:
        return render_template("post.html", form = form, loggedin = current_user.is_active)

#dashboard for users ,needs customization
@app.route('/dashboard')
@login_required
def dashboard():
    print(Users.query)
    return render_template("Dashboard.html", name = current_user.name, last_logged = current_user.last_login, profimage = current_user.profimage, description = current_user.description, views = current_user.profile_views, total_post = current_user.total_post, username = current_user.username, current_user = current_user)

#public profiles for each poster
@app.route('/dashboard/<poster>')
def public_user_dashboard(poster):
    user = Users.query.filter_by(username = poster).first()
    if user.is_anonymous == True:
        return render_template('public_profile.html', user = user)
    if current_user.is_active:
        if user.username == current_user.username:
            return redirect(url_for('dashboard'))
        elif current_user != user.username:
            user.profile_views += 1
            db.session.commit()
    return render_template('public_profile.html', user = user)

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

@app.route('/password_reset', methods = ["GET", "POST"])
def password_reset():
    form = Passwordrequest()
    if current_user.is_active:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        if request.method == "POST":
            try:
                user = Users.query.filter_by(email = form.email.data).first()
                send_mail(user)
                flash('Check your email. If your account is linked to this email a password change request will be sent.', 'success')
                return redirect(url_for('login'))
            except:
                flash('Check your email. If your account is linked to this email a password change request will be sent.', 'success')
                return redirect(url_for('login'))
    return render_template('password_reset.html', form = form)


@app.route('/password_reset/<token>', methods = ["GET", "POST"])
def reset_token(token):
    user = verify_token(token)
    if user == None:
        flash('The token is invalid or expired')
        return redirect(url_for('password_reset'))

    form = Passwordsuccess()
    if form.validate_on_submit():
        if request.method == 'POST':
            hashed_password=generate_password_hash(form.password.data, method = 'sha256')
            user.password = hashed_password
            db.session.commit()
        flash('Your password has been updated!','success')
        return redirect(url_for('login'))
    return render_template('confirm_reset.html', form = form)

#handles signup, checks database and returns messages
@app.route('/signup', methods = ["POST", "GET"])
def signup():
    form = Register()
    if form.validate_on_submit():
        if word_check(form.username.data) == True: # word filter
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
            hashed_password=generate_password_hash(form.password.data, method = 'sha256')  # if everything is valid, this hashes the password and stores it in database
            new_user = Users(name = form.name.data, username = form.username.data, password = hashed_password, email = form.email.data, date_joined = datetime.datetime.now().date(), profile_views = 0, total_post = 0)
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