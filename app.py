from datetime import datetime
#from enum import unique
#from flask_admin.actions import action
from flask_admin.base import AdminIndexView
#import flask_login
#from flask_login.mixins import AnonymousUserMixin
from flask import Flask, json, render_template, request, url_for, redirect, flash, jsonify, stream_with_context, Response, abort, make_response
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login.utils import login_required, login_user, logout_user
#from flask.sessions import NullSession
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin, LoginManager
#from flask_sqlalchemy.model import Model
from itsdangerous.serializer import Serializer
#from sqlalchemy.orm import dynamic_loader, relation, relationship, session
#from sqlalchemy.sql.functions import ReturnTypeFromArgs, user
#from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
#from werkzeug.datastructures import Authorization
#from wtforms.fields.core import BooleanField
#from wtforms.fields.simple import SubmitField
#from wtforms.validators import ValidationError
from models import Addprofile, LoginForm, Register, Postform, Addprofile, Passwordrequest, Passwordsuccess, Commentsform, Reportform
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pytz import timezone
from sqlalchemy.sql.expression import func
from flask_admin.contrib.fileadmin import FileAdmin
from flask_ipban import IpBan
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
#from gevent import monkey; monkey.patch_all()
#from gevent.pywsgi import WSGIServer
import pytz
import random
import datetime
import os 
import secrets
#import time
import os.path as op

app = Flask(__name__)
ip_ban = IpBan(ban_seconds=200)
ip_ban.init_app(app)

#route limiter if there someone decides to spam
limiter = Limiter(
    app,
    key_func=get_remote_address,
    #default_limits=["10000 per day", "100 per hour"]
)

ip_ban = IpBan(app)
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
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "basic"

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

#global variables
view_count = {}

class Users(UserMixin, db.Model): #user skeleton and columns for mysql database
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique = False)
    username = db.Column(db.String(25), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(50), unique = True)
    profimage = db.Column(db.String(255))
    hobbies = db.Column(db.String(255))
    description = db.Column(db.Text)
    date_joined = db.Column(db.String(50))
    last_login = db.Column(db.String(50))
    profile_views = db.Column(db.Integer)
    total_post = db.Column(db.Integer)
    posts = db.relationship('Posts', backref='poster', lazy = True) 
    comments = db.relationship('Comments', backref='commentor', lazy = True)
    likes = db.relationship('Posts', secondary=likes, lazy='subquery',
        backref=db.backref('liking', lazy=True))
    following = db.relationship(
                             'Users',
                             secondary=followers,
                             primaryjoin=(followers.c.follower_id == id),
                             secondaryjoin=(followers.c.followed_id == id),
                             backref= db.backref('followers', lazy=True), lazy=True,
                             )

    def is_admin(self):
        admins = ['henry']
        if self.username in admins:
            return True

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
    comments = db.relationship('Comments', backref = 'user_comments', lazy = False)
    genres = db.relationship('Categories', backref='genre', lazy=True, uselist = False)

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

class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_content = db.Column(db.Text)
    reporting_user = db.Column(db.String(255))
    title = db.Column(db.String(255))
    reason = db.Column(db.Text)
    date_reported = db.Column(db.String(255))

class Announcements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)


class MyModelView(ModelView): # modelview for admin
    def is_accessible(self):
        if current_user.is_admin():
            return True
        else:
            redirect(url_for('index'))
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    def delete_model(self, model): # overrided original delete method, now deletes previous comments and removes old lying image from static folder
        if hasattr(model,'image'):
            previous_category = model.genres[0]
            previous_comments = model.comments
            old_image = model.image # removes old photo from folder before updating
            for comments in previous_comments:
                self.session.delete(comments)
            self.session.delete(model)
            self.session.delete(previous_category)
            self.session.commit()
            path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
            os.remove(path)
            model.poster.total_post-=1
        else:
            self.session.delete(model)
            self.session.commit()
        return flash('Succesfully deleted post.', 'success')

class Files(FileAdmin): 
    def is_visible(self):
        if current_user.is_admin():
            return True
        return False

class allowedAdminView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_anonymous:
            return False
        return current_user.is_admin()



admin = Admin(app, index_view=allowedAdminView())
admin.add_view(MyModelView(Users, db.session))
admin.add_view(MyModelView(Posts, db.session))
admin.add_view(MyModelView(Comments, db.session))
admin.add_view(MyModelView(Reports, db.session))
admin.add_view(MyModelView(Announcements, db.session))
path = op.join(op.dirname(__file__), 'static/images')
admin.add_view(Files(path, name='Uploaded Images'))

#routes for backend, does not return templates. Routes are for JavaScript
@app.route('/likes/<post_id>', methods = ["GET", "POST"])
@limiter.limit("10/minute") 
@login_required
def likes(post_id):
    if request.method == "POST":
        current_posting =Posts.query.filter_by(id=post_id).first()
        current_posting.liking.append(current_user)
        db.session.commit()
        print('liked')
        return "Success"

@app.route('/dislikes/<post_id>', methods = ["GET", "POST"])
@limiter.limit("10/minute")
@login_required
def dislikes(post_id):
    if request.method == "POST":
        current_posting =Posts.query.filter_by(id=post_id).first()
        current_posting.liking.remove(current_user)
        db.session.commit()
        print("unliked")
        return "Success"

@app.route('/follow/<posting_user>', methods = ["GET","POST"])  #handles the following button with a js fetch request, this is where its routed to
@login_required
def followers(posting_user):
    if request.method == "POST":
        random_user = Users.query.get(posting_user)
        print(random_user)
        random_user.followers.append(current_user)
        db.session.commit()
        print('following')
    return "success"

@app.route('/unfollow/<posting_user>', methods = ["GET","POST"]) # reverse of the following button
@login_required
def unfollow(posting_user):
    if request.method == "POST":
        random_user = Users.query.get(posting_user)
        random_user.followers.remove(current_user)
        db.session.commit()
        print('unfollow')
    return "success"

@app.route('/comment_delete/<commentID>', methods = ["POST"]) # fetch route for deleting the comment
def delete_comment(commentID):
    if request.method == "POST":
        user_comment=Comments.query.get(commentID)
        db.session.delete(user_comment)
        db.session.commit()
    return "success"

@app.route('/edit_comment/<commentID>', methods = ['POST']) #fetch route for editing comment
def edit_comment(commentID):
    user_comment = Comments.query.get(commentID)
    new_comment = request.get_json(force = True)
    if request.method == "POST":
        user_comment.comment = new_comment
        db.session.add(user_comment)
        db.session.commit()
        return jsonify(user_comment.comment)
    return "success"

@app.route('/get_comment/<commentID>', methods = ["POST"]) #gets information for js to append into editing carrot in comment option
def getComment(commentID):
    comment = Comments.query.get(commentID)
    return jsonify(comment.comment)
#end non-template routes

#used my random generator to put in a hard guessable token to protect the url, also has login protection.
@app.route('/perm/j6*HOTk96RuvGq%mwlPUd^ViNa4jh3/<ID>', methods = ["GET", "POST"])
@login_required
def permanent(ID):
    deleting_user=Users.query.get(ID)
    all_users_post=Posts.query.filter_by(posting_user=deleting_user.username).all()
    postID = [posts.id for posts in all_users_post]  # list comprehension in order to get all ids in a list
    all_users_comments = Comments.query.filter_by(posting_user = deleting_user.username).all()
    if current_user.username is not deleting_user.username:
        return redirect(url_for('index'))
    if postID is not None:  
        for ids in postID:   # This loop begins to delete categories because its used as reference in a one to many for post
            category=Categories.query.filter_by(post_id = int(ids)).first() 
            db.session.delete(category)
        db.session.commit()
    if all_users_comments is not None:  # gets rid of all users comments on every post
        for comments in all_users_comments:
            db.session.delete(comments)
        db.session.commit()
    if all_users_post is not None:
        for posts in all_users_post:
            old_image = posts.image # removes old photo from folder 
            path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
            os.remove(path)
            for remaining_comments in posts.comments: # removes any remaining comments on the deleted posts
                db.session.delete(remaining_comments)
            db.session.delete(posts)
        db.session.delete(deleting_user) # deletes user after all table references and relationships are cleared.
        db.session.commit()
    flash('You have successfully deleted your account permanently.','logout')
    return redirect(url_for('login'))


def checkemail(): # checks email during signup
    user = Users.query.filter_by(email=request.form.get('email')).first()
    if user == None:
        return False
    else:
        return True

def checkusername(): #checks if username isn't appropriate during signup
    user = Users.query.filter_by(username = request.form.get('username')).first()
    if user == None:
        return False
    else:
        return True

def allowed_file(filename):  #splits file extension and checks if its allowed
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hex(file):  #returns hex name
    random_hex = secrets.token_hex(10)
    split=os.path.splitext(file)
    return random_hex + split[1]

def word_check(word_data):
    word_set = os.environ['Filtered_Words']
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

def send_mail(user):  #sends mail for password resets
    token = get_reset_token(user)
    print(token)
    message = Message('Password Reset Request', recipients = [user.email], sender='noreply@gmail.com')
    message.body= f'''
To Reset your password, click the following link:
{url_for('reset_token', token = token, _external = True)}
If you did not send this email, please ignore this message.
'''
    mail.send(message)

'''@app.route("/sse")
def sse():
    return render_template('ses.html')
    
@app.route("/listen")   #SSE(server sent events) setup if ever needed
def listen():

  def respond_to_client():
    while True:
        comment = Comments.query.all()
        if len(Comments.query.all()) != 1:
            for id in comment:
                print(id.id)
                _data = json.dumps=({'comment':str(id.id), "color":'red'})
                yield f"id: 1\ndata: {_data}\nevent: online\n\n"
        time.sleep(1)
  return Response(respond_to_client(), mimetype='text/event-stream')'''

  
#homepage
@app.route ('/')
def index():
    newest_announcement=Announcements.query.order_by(Announcements.id.desc()).first()
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
    return render_template("homepage.html", posts = posts, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, random_users_list = random_users_list, current_user = current_user, anonymous_check = current_user.is_anonymous, newest_announcement = newest_announcement)

@app.route('/report', methods = ['POST'])  #handles the report from posts.
@login_required
def report():
    report = request.get_json(force=True) # gets json dictionary 
    #print(report['reportingUser'], report['title'], report['reason'], report['postID'])  #checks json data if needed
    content = Posts.query.filter_by(id = report['postID']).first()
    completed_report = Reports(post_content = content.content, reporting_user = report['reportingUser'], title = report['title'], reason = report['reason'], date_reported = datetime.datetime.now().date())  # appends json key values into reports table
    db.session.add(completed_report)
    db.session.commit()
    return "success"

# individual user pagination
@app.route ('/user/<username>')
def all_post(username):
    newest_announcement=Announcements.query.order_by(Announcements.id.desc()).first()  
    hottest_post=db.session.query(func.max(Posts.article_views)).scalar()
    hottest_post_id=Posts.query.filter_by(article_views = hottest_post).first()
    page = request.args.get('page', 1, type = int)
    user = Users.query.filter_by(username = username).first()
    posts = Posts.query.filter_by(posting_user=user.username).order_by(Posts.id.desc()).paginate(page = page, per_page = 3)
    newest_user = Users.query.order_by(Users.id.desc()).all()
    newest_posts = Posts.query.order_by(Posts.id.desc()).first()   #all this is to get information about posts and page setup
    if posts.items == []:
        flash('You do not have any current post to show!', 'no_post')
        return redirect(url_for('dashboard'))
    return render_template("total_users_post.html", posts = posts, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, user = user, loggedin = current_user.is_active, newest_posts = newest_posts, newest_announcement = newest_announcement)

#category tags taken from homepage
@app.route ('/tag/<category>') 
def categories(category):
    newest_announcement=Announcements.query.order_by(Announcements.id.desc()).first()
    hottest_post=db.session.query(func.max(Posts.article_views)).scalar()
    hottest_post_id=Posts.query.filter_by(article_views = hottest_post).first()
    page = request.args.get('page', 1, type = int)
    posts = Categories.query.filter_by(category = category).order_by(Categories.id.desc()).paginate(page = page, per_page = 3)
    newest_user = Users.query.order_by(Users.id.desc()).all()
    newest_posts = Posts.query.order_by(Posts.id.desc()).first()
    if posts.items == []:  #if there are no items in that category, return alert
        flash('There are currently no post in that category.', 'no_post')
        return redirect(url_for('index'))
    return render_template("category_tag.html", posts = posts, current_date = datetime.datetime.now().date(), newest_user = newest_user, hottest_post_id = hottest_post_id, loggedin = current_user.is_active, newest_posts = newest_posts, category = category, newest_announcement = newest_announcement)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_profile():
    profile = Addprofile()
    user = Users.query.get(current_user.id)
    if request.method == 'POST':  #checks all the data that has been submitted 
        if 'file' not in request.files: #check if the post request has a file
            flash('There was not file uploaded!', 'no_file')
            return redirect(request.url)
        file = request.files['file'] # gets file if everything is valid
        if profile.description.data and profile.hobbies.data and file and allowed_file(file.filename) == True: #function to update all three at once
                filename = secure_filename(file.filename)
                hexed_name = hex(filename) # passes original name of file and turns turns name into hex, prevents long names and overloads
                output_size = (300,300)
                picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
                picture.thumbnail(output_size, Image.ANTIALIAS)
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
                user.profimage = hexed_name
                user.description = profile.description.data
                user.hobbies = profile.hobbies.data
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully changed your profile picture, hobbies and profile description.','prof_photo')
                return redirect(url_for('dashboard', name=filename))
        if profile.description.data or profile.hobbies.data != '': # if theres info inside of these description or hobby box, it will check for which
            if profile.description.data != '' and profile.hobbies.data == '' : # if description is the only thing with info, it will only update this
                user.description = profile.description.data
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully changed your profile description!', 'prof_description')
                return redirect(url_for('dashboard'))
            elif profile.description.data =='' and profile.hobbies.data != '': # if hobbies is the only thing with info, it will update only the hobbies.
                user.hobbies = profile.hobbies.data
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully changed your hobbies', 'prof_description')
                return redirect(url_for('dashboard'))
            elif profile.description.data and profile.hobbies.data != '': # if hobbies is the only thing with info, it will update only the hobbies.
                user.hobbies = profile.hobbies.data
                user.description = profile.description.data
                db.session.add(user)
                db.session.commit()
                flash('You have sucessfully changed your hobbies and description', 'prof_description')
                return redirect(url_for('dashboard'))
        if 'file' not in request.files: #check if the post request has a file
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
            else: # handles the removal of an already existing profile.
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
    profile.description.data = user.description
    profile.hobbies.data = user.hobbies
    return render_template('upload.html', profile = profile)

#post editing needs work to protect url numbers
@app.route('/edit/<postID>', methods = ["POST", "GET"])
@login_required
def edit(postID):
    form = Postform()
    current_blog = Posts.query.get(postID)
    if current_blog is None:
        flash('This post does not exist','false_user')
        return redirect(url_for('index'))
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
    if current_user.username != poster.posting_user: #route protection if user is not original poster
        flash('You can only delete your own post.', 'false_user')
        return redirect(url_for('index'))
    try:
        delete_id = Posts.query.get(postID)
        category_id = Categories.query.filter_by(post_id = delete_id.id).first()
        current_user.total_post -= 1
        for comments in delete_id.comments:
            db.session.delete(comments)
        db.session.delete(delete_id)
        db.session.delete(category_id)
        db.session.commit()
        old_image = delete_id.image # removes old photo from folder before updating
        path = os.path.join(app.config['UPLOAD_FOLDER'], old_image)
        os.remove(path)
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
    postid=Posts.query.get(postID)
    json_postid = {"postID":postid.id}#json object
    form = Commentsform()
    if current_user.get_id() == None:
        pass
    elif current_user.username != original_poster.posting_user:
        if current_user.email not in view_count:
            view_count[str(current_user.email)] = []
        if postID not in view_count.get(str(current_user.email)):      
            expanded_post.article_views += 1
            view_count[str(current_user.email)].append(postID)
            db.session.commit()
    if request.method == "POST":
        date = datetime.datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))
        comment = Comments(comment=form.comment.data, post_id = postID, date = date.strftime("%m/%d/%y %I:%M%p"), posting_user = current_user.username, poster_id = current_user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('expanded_post', postID = postID))
        #poster_image = current_user.profimage
    return render_template('expanded_post.html', expanded_post = expanded_post, form = form, show_comments = show_comments, loggedin = current_user.is_active, current_user_check = current_user.is_anonymous, current_user = current_user, likes = len(number_of_likes), liked = number_of_likes, user = current_user, json_postid = json_postid) # current_user doesn't work if changed to check if user is active. So i passed two variables instead to check for if the user exist and then the method to call image

#posting for blog articles/status
@app.route('/post', methods = ["POST", "GET"])
@login_required
def post():
    form = Postform()
    if request.method == "POST":
        #check if the post request has the file
        if 'file' not in request.files:
            flash('No file part', 'posted')
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
            output_size = (500,500)
            picture = Image.open(file)   # converts uploaded images into smaller thumbnails or any pixel related size
            picture.thumbnail(output_size, Image.ANTIALIAS)
            picture.save(os.path.join(app.config['UPLOAD_FOLDER'], hexed_name), quality = 100)
            posting = Posts(title = form.title.data, content = form.content.data, image = hexed_name, posting_user = current_user.username, date_posted = datetime.datetime.now().date(), article_views = 0, poster_id = current_user.id, likes = 0, dislikes = 0)
            current_user.total_post += 1
            db.session.add(posting)
            db.session.commit()
            postid = Posts.query.filter_by(content = form.content.data, posting_user = current_user.username).first()
            category= Categories(category = request.form['genre'], post_id = postid.id)
            db.session.add(category)
            db.session.commit()
            #new_post_id = Posts.query.filter_by(image = hexed_name, posting_user = current_user.username).first()
            #new_post_id.liking.append(current_user)
            db.session.commit()
            flash('Your post has been added', 'posted')
            return redirect(url_for('post'))
        flash('Your file extension is not allowed', 'posted')
        return redirect(url_for('post'))
    else:
        return render_template("post.html", form = form, loggedin = current_user.is_active)

#dashboard for users ,needs customization
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("Dashboard.html", last_logged = current_user.last_login, current_user = current_user, follower_count = len(current_user.followers))

#public profiles for each poster
@app.route('/public_dashboard/<poster>')
def public_user_dashboard(poster):
    user = Users.query.filter_by(username = poster).first()
    if user == None:
        flash('There is no user with that username.','no_post')
        return redirect(url_for('index'))
    #top_post=db.session.query(func.max(Posts.article_views)).all()
    top_post=db.session.query(func.max(Posts.article_views)).filter_by(posting_user=user.username).scalar()
    top_article = Posts.query.filter_by(posting_user = user.username, article_views = top_post).first()
    #print(top_article)
    if user.is_anonymous == True:
        return render_template('public_profile.html', user = user)
    if current_user.is_active:
        if user.username == current_user.username:
            return redirect(url_for('dashboard'))
        if current_user != user:
            if current_user.email not in view_count:
                view_count[str(current_user.email)] = []
            if poster not in view_count.get(str(current_user.email)):
                user.profile_views += 1
                view_count[str(current_user.email)].append(user.username)
            db.session.commit()
    return render_template('public_profile.html', user = user, user_followers = len(user.followers), current_user = current_user, top_article = top_article)

#login method/handler
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
                view_count[str(current_user.email)] = []
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
    if str(current_user.email) in view_count:
        view_count.pop(str(current_user.email)) # takes user out of viewcount dict
    logout_user()
    flash('You have been successfully logged out', 'logout')
    return redirect(url_for("login"))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    #http_server = WSGIServer(("localhost", 5000), app)
    #http_server.serve_forever()