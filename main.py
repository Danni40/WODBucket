from flask import Flask, request, redirect, render_template, session, flash, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from random import randint
import traceback
import datetime
import cgi

#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient('mongodb://127.0.0.1:27017/test')
db=client.wod_test


app = Flask(__name__, static_url_path = "", static_folder = "static")
app.config['DEBUG'] = True
app.config['STATIC_FOLDER'] = '/static'

class User:

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.logged_in = False

@app.route("/images")
def images():
    return render_template('index.html')

@app.route("/stylesheets")
def stylesheets():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['logged_in'] = False
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_count=db.register.find( {'email': email } ).count()
        if user_count == 1:
            user = db.register.find_one({'email':email})
            #password=user.get('password')

            if password == user.get('password'):
                session['user'] = username
                session['logged_in'] = True
                flash('welcome back, '+ username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/update", methods=['GET', 'POST'])
def update():
    exercise1_error=''
    exercise2_error=''
    exercise3_error=''
    username = db.register.find_one({'username': session['user']})
    try:
        if request.method == 'POST':
            
            date = request.form['date']
            exercise1 = request.form['exercise1']
            exercise2 = request.form['exercise2']
            exercise3 = request.form['exercise3']
            exercise1_num = request.form['exercise1_num']
            exercise2_num = request.form['exercise2_num']
            exercise3_num = request.form['exercise3_num']
            workout = {
            "username": username.get('username'),
            'date' : datetime.datetime.utcnow(),
            'exercises': {exercise1: exercise1_num, exercise2: exercise2_num, exercise3:exercise3_num}
            }

            if not exercise1:
                exercise1_error='Exercise #1 not entered'

            if not exercise2:
                exercise2_error='Exercise #2 not entered'

            if not exercise3:
                exercise3_error='Exercise #3 not entered'

            if not exercise1_error and not exercise2_error and not exercise3_error:
                result=db.workouts.insert_one(workout)
                workouts = db.workouts.find({'username':username})
                workout_id = db.workouts.find_one({'workouts._id': result.inserted_id})
                return redirect("/")

            else:
                return redirect('/', exercise1_error=exercise1_error, exercise2_error=exercise2_error, exercise3_error=exercise3_error)
            
        else:
            render_template('index.html')

    except Exception:
            traceback.print_exc()

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
        existing_user = db.register.count( {'email': email } )
        if existing_user > 0:
            flash('yikes! "' + email + '" is already taken "')
            return redirect('/signup')
        username_db_count = db.register.count( { 'username' : username} )
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
        }
        #db.session.add(user)
        result=db.register.insert_one(user)
        #db.session.commit()
        session['user'] = username
        session['logged_in'] = True
        return render_template('index.html')
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
    return redirect("/")

@app.route('/', methods=['GET','POST'])
def index():
    if ('user' in session):
        username = session['user']
        userWorkoutsCount = db.workouts.count({'username': username})
        userWorkouts = db.workouts.find({'username': username})
        now = datetime.datetime.now()
        lastEntry = db.workouts.find({'username': username}).limit(1).sort("_id",-1)
        return render_template('index.html', now=now.date(), userWorkoutsCount=userWorkoutsCount, userWorkouts=userWorkouts, username=username, lastEntry=lastEntry)
    else:
        now = datetime.datetime.now()
        return render_template('index.html', now=now.date())
    #return render_template('workout.html')

    

@app.route("/workout", methods=['GET','POST'])
def workout():
    if request.args.get('id'):
        username = session['user']
        _id = "ObjectId('" + request.args.get('id') + "')"
        workout_id = request.args.get('id')
        userWorkoutsCount = db.workouts.count({'username': username})
        userWorkouts = db.workouts.find({'username': username})
        workout = db.workouts.find_one({'_id': _id})
        [i for i in db.workouts.find({"_id": ObjectId(request.args.get('id'))})]
        return render_template("workout.html", i=i, workout=workout, _id=_id, userWorkoutsCount=userWorkoutsCount, userWorkouts=userWorkouts, username=username)


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

endpoints_without_login = ['login', 'signup','index', 'static', 'images', 'stylesheets']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")

app.secret_key = 'dksfmskfslvnmksmkslmgskldm'

if __name__ == '__main__':
    app.run()