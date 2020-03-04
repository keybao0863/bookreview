import os

from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signon", methods=["GET","POST"])
def signon():
    #If user is signing on, check if username already in use, otherwise, add user
    # to database.
    if(request.method=="POST"):
        #first check if user is in databse, if so, ask user to sign in instead
        user = db.execute("SELECT * FROM users WHERE username = :u", {"u":request.form['username']}).fetchone()

        if(user):
            #if user exists, ask user to signin
            return render_template("signin.html", username = request.form['username'])
        else:
            #If user does not exist, add user to database.
            db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
            {"username":request.form['username'], "email":request.form['email'],"password":request.form['password']})
            print("added user")
            db.commit()
            return render_template("signin.html")

    return render_template("signon.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    #Check if user exists and if password match
    if(request.method=="POST"):
        username = request.form['username'];
        user = db.execute("SELECT * FROM users WHERE username = :u",
        {"u":request.form['username']}).fetchone()

        #check if user exists.
        if(user):
            input_password = request.form['password'];
             #If user exists,check if password matches
            if(user.password==input_password):
                #If password is correct, log user_id in session.
                session['logged_in'] = True
                session['used_id'] = user.id
                print("logged in")
                return render_template("index.html")
            else:
                #If password is not correct, return to signin page.
                print("Password not correct")
                return render_template("signin.html")
        else:
            print("User does not exist.")
            return render_template("signin.html")
    else:
        return render_template("signin.html")

@app.route("/logoff")
def logoff():
    session['logged_in'] = False
    session['user_id'] = None
    return index();
