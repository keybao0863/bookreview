import os

from flask import Flask, session, render_template, request
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
