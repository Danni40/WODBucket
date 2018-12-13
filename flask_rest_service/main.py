from flask import Flask, request, redirect, render_template, session, flash, url_for
from pymongo import MongoClient
from random import randint
import traceback
import datetime
import cgi
import json
from flask import request, abort
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_rest_service import app, api, mongo
from bson.objectid import ObjectId
import requests

class User:

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.logged_in = False

#add route for images
@app.route("/images")
def images():
    return render_template('index.html')

#add route for stylesheets
@app.route("/stylesheets")
def stylesheets():
    return render_template('index.html')

#code login routing
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        session['logged_in'] = False
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_count=mongo.db.register.find( {'email': email } ).count()
        if user_count == 1:
            user = mongo.db.register.find_one({'email':email})

            if password == user.get('password'):
                session['user'] = username
                session['logged_in'] = True
                flash('welcome back, '+ username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

#code update workout
@app.route("/update", methods=['GET', 'POST'])
def update():
    #handle errors and input validation
    exercise1_error=''
    exercise2_error=''
    exercise3_error=''
    username = mongo.db.register.find_one({'username': session['user']})
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
                result=mongo.db.workouts.insert_one(workout)
                workouts = mongo.db.workouts.find({'username':username})
                workout_id = mongo.db.workouts.find_one({'workouts._id': result.inserted_id})
                return redirect("/")

            else:
                flash('Please enter some exercises' + username)
                return render_template('index.html')
            
        #else:
            #return render_template('index.html')

    except Exception:
            traceback.print_exc()

#code signup page and route appropriately
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
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        existing_user = mongo.db.register.count( {'email': email } )
        if existing_user > 0:
            flash('yikes! "' + email + '" is already taken "')
            return redirect('/signup')
        username_db_count = mongo.db.register.count( { 'username' : username} )
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken "')
            return redirect('/signup')     
        if ' ' in username or ' ' in email or ' ' in password:
            flash('Username, email or password cannot contain any spaces.')
            return redirect('/signup')
        if len(username) < 3 or len(username) > 20:
            flash('Username must meet length requirements')
            return redirect('/signup')
        name_error="That's not a valid username"
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')

        user = {
        'username' : username,
        'email' : email,
        'password' : password,
        }
        result=mongo.db.register.insert_one(user)
        session['user'] = username
        session['logged_in'] = True
        return redirect('/')
    else:
        return render_template('signup.html')

#handle input validation
def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

#code logout and route appropriately
@app.route("/logout", methods=['POST'])
def logout():
    session.pop('logged_in', None)
    del session['user']
    return redirect("/")

#create the index route
@app.route('/', methods=['GET','POST'])
def index():
    if ('user' in session):
        #get workouts for the specific user
        username = session['user']
        userWorkoutsCount = mongo.db.workouts.count({'username': username})
        userWorkouts = mongo.db.workouts.find({'username': username})
        now = datetime.datetime.now()
        lastEntry = mongo.db.workouts.find({'username': username}).limit(1).sort("_id",-1)
        
        #populate the recommended workout
        cardio = ['Walk','Bike','Run', 'Skate', 'Swim','Jump Rope','Row', 'Stair Climber','Sprint', 'Elliptical','Spike Ball','Interval Run', 'Ergo']
        strength = ['Kettlebell Swing','Deadlift','Front Squat','Back Squat','Overhead Squat', 'Benchpress', 'Pullup', 'Wall Ball', 'Pushup', 'Rope Climb']
        balance_and_stretching = ['Balance Walk', 'One Foot Stand', 'Front Arm Raise', 'Calf Stretch', 'Lower Back Stretch', 'Thigh Stretch', 'Neck Rotation', 'Chest Stretch','Yoga Stretch','Back Stretch']
        exercise1 = cardio[randint(0, (len(cardio)-1))]
        exercise2 = strength[randint(0, (len(strength)-1))]
        exercise3 = balance_and_stretching[randint(0,  (len(balance_and_stretching)-1))]
        exercise1_num = str(randint(1, 5)) + ' miles'
        exercise2_num =  str(randint(12, 15)) + ' reps for ' + str(randint(1, 3)) + ' sets'
        exercise3_num =  str(randint(3, 5)) + ' minutes'
        return render_template('index.html', now=now.date(), userWorkoutsCount=userWorkoutsCount, userWorkouts=userWorkouts, username=username, lastEntry=lastEntry, exercise1=exercise1, exercise2=exercise2, exercise3=exercise3, exercise1_num=exercise1_num, exercise2_num=exercise2_num, exercise3_num=exercise3_num)
    #C:\Users\the_c\OneDrive\Documents\691-Capstone\WODBucket\WODBucket\templates\index.html
    else:
        now = datetime.datetime.now()
        return render_template('index.html', now=now.date())

#have a page individual workouts to show
@app.route("/workout", methods=['GET','POST'])
def workout():
    if not request.args:
        username = session['user']
        userWorkouts = mongo.db.workouts.find({'username': username})
        [i for i in mongo.db.workouts.find({"username": username})]
        return render_template("workouts.html", username=username, userWorkouts=userWorkouts)
    
    if request.args.get('id'):
        username = session['user']
        _id = "ObjectId('" + request.args.get('id') + "')"
        workout_id = request.args.get('id')
        userWorkoutsCount = mongo.db.workouts.count({'username': username})
        userWorkouts = mongo.db.workouts.find({'username': username})
        workout = mongo.db.workouts.find_one({'_id': _id})
        i = mongo.db.workouts.find({"_id": ObjectId(request.args.get('id'))})
        return render_template("workout.html", i=i, workout=workout, _id=_id, userWorkoutsCount=userWorkoutsCount, userWorkouts=userWorkouts, username=username)

#have a page for all workouts to show
@app.route("/workouts", methods=['GET'])
def workouts():
    return render_template("workouts.html", username=username, userWorkouts=userWorkouts)

#allow only certain pages to be accessible when not logged in
endpoints_without_login = ['login', 'signup','index', 'static', 'images', 'stylesheets']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/")

#in production, provide a unique key for security
app.secret_key = 'dksfmskfslvnmksmkslmgskldm'

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)