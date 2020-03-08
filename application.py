import os

from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.secret_key = os.urandom(12)

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
            flash("added user")
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
                session['user_id'] = user.id
                flash("you are logged in")
                return render_template("search.html")
            else:
                #If password is not correct, return to signin page.
                flash("Password not correct")
                return render_template("signin.html")
        else:
            flash("User does not exist.")
            return render_template("signin.html")
    else:
        return render_template("signin.html")

@app.route("/logoff")
def logoff():
    session.pop('user_id', None)
    return index();

@app.route("/search", methods=['GET', 'POST'])
def search():
    #Process POST request
    if(request.method=="POST"):
        option = request.form['search_option'].lower()
        #Search also for partially matched queries
        query = '%' + request.form['search_box'].lower() + '%'
        books = db.execute("SELECT * FROM books WHERE lower(" + option + ") LIKE :q",
        {"o": option, "q":query}).fetchall()

        #If no book is found, return an error, otherwise, display results
        if(len(books)==0):
            flash("No book match is found")
            return render_template("search.html")

        return render_template("search_result.html", books = books)

    #Check if the user is logged in, if not, ask the user to log in.
    if('user_id' not in session):
        return signin()
    #If user has logged in, go to search page
    else:
        return render_template("search.html")

@app.route("/books/<int:book_id>")
def book(book_id):
    #Make sure book exists
    book = db.execute("SELECT * FROM books WHERE id = :i", {'i':book_id}).fetchone()
    if book is None:
        return render_template("error.html", message = "Book does not exist")

    #If book exists, serve book info and reviews

    # TODO: get reviews
    return render_template("book.html", book=book)

@app.route("/review/<int:book_id>", methods=['POST'])
def review(book_id):
    #Make sure user is logged on
    if('user_id' not in session):
        return render_template("error.html", message= "You need to log in first.")

    #Deposit review in databse
    user_id = session['user_id']
    rating = request.form['rating']
    review = request.form['review']

    db.execute("INSERT INTO reviews (book_id, user_id, rating, review) VALUES \
    (:book_id, :user_id, :rating, :review)", {'book_id':book_id, 'user_id': user_id,
    'rating':rating, 'review': review})
    db.commit()
    flash("Reviewed successfully")
    return book(book_id)
