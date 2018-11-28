from flask import Flask, request, redirect, render_template, session, flash, url_for
from pymongo import MongoClient
from random import randint
import traceback
import cgi

#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient('mongodb://127.0.0.1:27017/test')
db=client.wod_test


app = Flask(__name__)
app.config['DEBUG'] = True

class User:


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.logged_in = False

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['logged_in'] = False
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                session['logged_in'] = True
                flash('welcome back, '+ user.username)
                return redirect("/newblog")
        flash('bad username or password')
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if username == '' or email == '' or password == '' or verify == '':
            flash('Sorry! Cannot have any blank fields')
            return redirect('/signup')
        #existing_user = User.query.filter_by(email=email).first()
        #TODO  Work on the db connections
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        existing_user = db.register.find_one( {email: email } )
        if existing_user > 0:
            flash('yikes! "' + email + '" is already taken "')
            return redirect('/signup')
        username_db_count = db.register.find_one( { 'username' : username} )
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken "')
            return redirect('/signup')     
        if ' ' in username or ' ' in email or ' ' in password:
            flash('Username, email or password cannot contain any spaces.')
            return redirect('/signup')
        if len(username) < 3 or len(username) > 20:
            flash('Password must meet length requirements')
            return redirect('/signup')
        name_error="That's not a valid username"
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        #user = User(username=username, email=email, password=password)
        user = {
        'username' : username,
        'email' : email,
        'password' : password,
        'exercises' : []
        }
        #db.session.add(user)
        result=db.register.insert_one(user)
        #db.session.commit()
        session['user'] = username
        session['logged_in'] = True
        return render_template('workout.html')
    else:
        return render_template('signup.html')

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    del session['user']
    return redirect("/blog")

@app.route('/', methods=['GET','POST'])
def index():

    #users = db.register.find( { } )
    #return render_template('index.html', users=users)

    return render_template('workout.html')

@app.route("/blog", methods=['GET','POST'])
def blog():
    if not request.args:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs)
    elif request.args.get('id'):
        user_id = request.args.get('id')
        blog = Blog.query.filter_by(id=user_id).first()
        user = User.query.filter_by(id=user_id).first()
        return render_template('blogpost.html', blog=blog, user=user)
    elif request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.filter_by(id=user_id).first()
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user.html', blogs=blogs, user=user)

@app.route("/newblog", methods=['POST', 'GET'])
def index2():
    title_error=''
    body_error=''
    blogs = Blog.query.all()
    owner = User.query.filter_by(username=session['user']).first()
    print(blogs)

    try:
        if request.method == 'POST':

            blog_body = request.form['blog_body']
            blog_name = request.form['blog_name']

            new_blog = Blog(blog_name, blog_body, owner)
            db.session.add(new_blog)
            

            if not blog_name:
                title_error='no blog title entered'

            if not blog_body:
                body_error='no blog body entered'

            if not title_error and not body_error:
                db.session.commit()
                blog_id = new_blog.id
                return redirect('/blog?id={blog_id}'.format(blog_id=blog_id))

            else:

                return render_template('newblog.html', title="New Blog", blogs=blogs, 
                    body_error=body_error, title_error=title_error, blog_body=blog_body, blog_name=blog_name, owner=owner)

        else:
            return render_template('newblog.html', title="New Blog", blogs=blogs,)
            
    except Exception:
            traceback.print_exc()

endpoints_without_login = ['login', 'signup','index', 'blog']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")

app.secret_key = 'dksfmskfslvnmksmkslmgskldm'

if __name__ == '__main__':
    app.run()