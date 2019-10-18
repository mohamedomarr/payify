import os
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, email_check, reg_mail, trans_mail

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/")
def nothing():
    """no url route"""

    return redirect("/dashboard")


@app.route("/home")
def home():
    """Home Page"""

    return render_template("home.html")


@app.route("/dashboard")
@login_required
def index():
    """user's Dashboard"""

    # Get user's First and last name for Navbar and user's cash for balance
    user = db.execute("SELECT first, last, cash FROM users WHERE id = :userid",userid=session["user_id"])
    
    # Query for user's recent activity
    trans1 = db.execute("SELECT first, last, date, type, gross, transid FROM trans INNER JOIN users ON trans.user2id = users.id WHERE trans.id  = :userid"
                        , userid=session["user_id"])

    # reverse recent activity
    trans = trans1[::-1]

    return render_template("index.html", user=user, trans=trans)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email").lower())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            classs = "alert-danger"
            return render_template("login.html", classs=classs)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Register user"""
    if request.method == "POST":

        # Ensure first name isn't blank
        if not request.form.get("first_name"):
            return apology("missing first name", 403)

        # Ensure last name isn't blank
        if not request.form.get("last_name"):
            return apology("missing last name", 403)

        # Ensure email isn't blank
        if not request.form.get("email"):
            return apology("Missing Email", 403)

        # Ensure password isn't blank
        if not request.form.get("password"):
            return apology("missing password")

        # Ensure passwords is match
        if request.form.get("password") != request.form.get("confrim_password"):
            flash("Passwords don't match")
            classs = "alert-danger"
            return render_template("signup.html", classs=classs)

        email = request.form.get("email").lower()
        # Check Email is valid
        checking = email_check(email)

        if checking == False:
            flash("invalid Email Address")
            classs = "alert-danger"
            return render_template("signup.html", classs=classs)

        # Ensure email isn't already exists
        result = db.execute("SELECT email FROM users WHERE email = :email",
                            email=email)

        if len(result) == 1:
            flash("Email isn't avaliable")
            classs = "alert-danger"
            return render_template("signup.html", classs=classs)

        # Encrypt user's password
        hash = generate_password_hash(request.form.get("password"))

        # Insert user's inputs into DataBase
        db.execute("INSERT INTO users (email, hash, first, last) VALUES(:email, :hash, :first, :last)",
                   email=email, hash=hash, first=request.form.get("first_name"), last=request.form.get("last_name"))

        # Query database for user's id
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # send a Welcome email
        reg_mail(request.form.get("email"), request.form.get("first_name"))

        flash('Welcome!')

        # Redirect user to home page
        return redirect("dashboard")

    else:
        return render_template("signup.html")


@app.route("/transfer", methods=['GET', 'POST'])
@login_required
def transfer():
    """transfer money"""
    # Get user's First and last name for Navbar and user's email, cash for transfer mail
    user = db.execute("SELECT first, last, email, cash FROM users WHERE id = :userid",userid=session["user_id"])

    if request.method == "POST":

        # Check email isn't blank
        if not request.form.get("email"):
            return apology("Missing Email", 400)

        # Check amount of cash isn't blank
        if not request.form.get("cash"):
            return apology("missing amount of cash", 400)
        else:
            # else put inputed cash, mail into variables
            cash = request.form.get("cash")
            email = request.form.get("email").lower()

        # Check Email is valid
        checking = email_check(email)

        if checking == False:
            flash("Email isn't valid")
            classs = "alert-danger"
            return render_template("transfer.html", classs=classs, user=user)

        # Ensure email isn't users's one
        if request.form.get("email") == user[0]['email']:
            flash("You can't send to yourself")
            classs = "alert-danger"
            return render_template("transfer.html", classs=classs, user=user)

        # Ensure the email is exists
        result = db.execute("SELECT * FROM users WHERE email = :email",
                            email=email)

        if len(result) != 1:
            flash("Email isn't exists")
            classs = "alert-danger"
            return render_template("transfer.html", classs=classs, user=user)
        
        # if the inputed email is exsist and valid get his user id in user2id variable
        else:
            user2id = result[0]["id"]

        # Check user can afford
        if float(cash) > user[0]["cash"]:
            flash("You cannot afford")
            classs = "alert-danger"
            return render_template("transfer.html", classs=classs, user=user)

        # Get the current Date and Time
        now = datetime.datetime.now()
        date = now.strftime("%d %b %Y")
        time = now.strftime("%H:%M:%S")

        # Get the fees amount and the netcash (cash - fees)
        fee_cash = float(cash) * 0.01
        fee = round(fee_cash,2)
        
        netcash = float(cash) - fee

        # Update user's amount of cash (sender)
        db.execute("UPDATE users SET cash = cash - :cash WHERE id = :userid", cash=cash, userid=session["user_id"])

        # Update user's amount of cash (reciver)
        db.execute("UPDATE users SET cash = cash + :netcash WHERE id = :userid", netcash=netcash, userid=user2id)

        # Insert transaction to  db part1 (sender side)
        db.execute("INSERT INTO trans (id, user2id, type, gross, fee, netcash, date, time) VALUES (:userid, :user2id, 'to', -:gross, :fee, -:netcash, :date, :time)",
                   userid=session["user_id"], user2id=user2id, gross=cash, fee=fee, netcash=cash, date=date, time=time)

        # Get mail (sender side) details
        sender_mail = user[0]['email']
        reciver_details = {'first': result[0]["first"], 'last': result[0]["last"], 'email': email}
        trans_sender = {'gross': '%.2f' % float(cash), 'fee': '%.2f' % float(fee), 'netcash': '%.2f' % float(cash), 'date': date, 'time': time, 'type': 'sent', 'type2': 'to',
                        'subject': "Your payment has completed", 'header': "received from"}
        
        # Send email to the sender
        trans_mail(sender_mail, reciver_details, trans_sender)

        # Insert transaction to  db part2 (reciver side)
        db.execute("INSERT INTO trans (id, user2id, type, gross, fee, netcash, date, time) VALUES (:user2id, :userid, 'from', :gross, -:fee, :netcash, :date, :time)",
                   user2id=user2id, userid=session["user_id"], gross=cash, fee=fee, netcash=netcash, date=date, time=time)

        # Get mail (reciver side) details
        reciver_mail = email
        sender_details = {'first': user[0]["first"], 'last': user[0]["last"], 'email': user[0]['email']}
        trans_reciver = {'gross': '%.2f' % float(cash), 'fee': '%.2f' % float(fee), 'netcash': '%.2f' % float(netcash), 'date': date, 'time': time, 'type': 'received', 'type2': 'from',
                        'subject': "You've got money", 'header': "sent"}
        # Send email to the reciver
        trans_mail(reciver_mail, sender_details, trans_reciver)

        flash("Money Transferred Successfully")
        return redirect("/")

    else:
        return render_template("transfer.html", user=user)


@app.route("/transactions")
@login_required
def transactions():
    """transactions list"""
    
    # Get user's First and last name for Navbar
    user = db.execute("SELECT first, last FROM users WHERE id = :userid", userid=session["user_id"])
    
    # Query DataBase for Transactions list
    trans1 = db.execute("SELECT first, last, date, type, gross, transid FROM trans INNER JOIN users ON trans.user2id = users.id WHERE trans.id  = :userid",
                        userid=session["user_id"])

    # reverse recent activity
    trans = trans1[::-1]

    return render_template("transactions.html", user=user, trans=trans)


@app.route("/payment", methods=["GET"])
@login_required
def payment():
    """Payment Details Page"""

    #Get user's First and last name for Navbar
    name = db.execute("SELECT first, last FROM users WHERE id = :userid", userid=session["user_id"])

    # Get transaction or payment id from args
    payment_id = request.args.get('id')
    
    # Check that if args isn't include payment id
    if not request.args.get('id'):
        return apology('Not found', 404)

    # Query DataBase for transactions Details
    details = db.execute("SELECT * FROM trans INNER JOIN users ON trans.user2id = users.id WHERE transid = :payment_id"
                         , payment_id=payment_id)

    return render_template("payment.html", name=name, details=details)


@app.route("/settings")
@login_required
def settings():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = db.execute("SELECT first, last, email FROM users WHERE id = :userid", userid=session["user_id"])

    if request.method == "POST":

        return render_template("settings.html")

    else:
        return render_template("settings.html", name=name)


@app.route("/settings/name", methods=["GET", "POST"])
@login_required
def name():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = db.execute("SELECT first, last FROM users WHERE id = :userid", userid=session["user_id"])

    if request.method == "POST":

        # Ensure first name isn't blank
        if not request.form.get("first_name"):
            return apology("missing firstname")

        # Ensure last name isn't blank
        if not request.form.get("last_name"):
            return apology("missing")

        # Ensure Password isn't blank
        if not request.form.get("password"):
            return apology("missing")

        # Query Database for user's hash
        rows = db.execute("SELECT hash FROM users WHERE id = :userid",
                          userid=session["user_id"])

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid current password")
            classs = "alert-danger"
            return render_template("change_name.html", classs=classs, name=name)

        # update user's first, last name
        db.execute("UPDATE users SET first = :first, last = :last WHERE id = :userid",
                   first=request.form.get("first_name"), last=request.form.get("last_name"), userid=session["user_id"])
        
        flash("Name Changed Successfully")
        return redirect("/settings")

    else:
        return render_template("change_name.html", name=name)


@app.route("/settings/email", methods=["GET", "POST"])
@login_required
def email():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = db.execute("SELECT first, last, email FROM users WHERE id = :userid", userid=session["user_id"])

    if request.method == "POST":

        # Ensure first email isn't blank
        if not request.form.get("email"):
            return apology("missing email")
        
        # Ensure first password isn't blank
        if not request.form.get("password"):
            return apology("missing password")
        
         # Check Email is valid
        email = request.form.get("email").lower()
        checking = email_check(email)

        if checking == False:
            flash("invalid Email Address")
            classs = "alert-danger"
            return render_template("change_email.html", classs=classs, name=name)
        
        # Ensure email isn't already exists
        result = db.execute("SELECT email FROM users WHERE email = :email",
                            email=email)

        if len(result) == 1:
            flash("Email Address isn't avaliable")
            classs = "alert-danger"
            return render_template("change_email.html", classs=classs, name=name)
        
        # Query Database for user's hash
        rows = db.execute("SELECT hash FROM users WHERE id = :userid",
                          userid=session["user_id"])

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid current password")
            classs = "alert-danger"
            return render_template("change_email.html", classs=classs, name=name)

        # update user's Email
        db.execute("UPDATE users SET email = :email WHERE id = :userid",
                   email=email, userid=session["user_id"])
        
        flash("Email Changed Successfully")
        return redirect("/settings")

    else:
        return render_template("change_email.html", name=name)


@app.route("/settings/password", methods=["GET", "POST"])
@login_required
def password():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = db.execute("SELECT first, last FROM users WHERE id = :userid", userid=session["user_id"])

    if request.method == "POST":

        # Ensure old password isn't blank
        if not request.form.get("old_password"):
            return apology("missing old password")

        if not request.form.get("password"):
            return apology("missing password")

        # Ensure passwords are match
        if request.form.get("password") != request.form.get("confrim_password"):
            flash("Passwords don't match")
            classs = "alert-danger"
            return render_template("change_password.html", classs=classs, name=name)

        # Query Database for user's hash
        rows = db.execute("SELECT hash FROM users WHERE id = :userid",
                          userid=session["user_id"])

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            flash("invalid current password")
            classs = "alert-danger"
            return render_template("change_password.html", classs=classs, name=name)

        # Encrypt user's password
        hash = generate_password_hash(request.form.get("password"))

        # update user's password
        db.execute("UPDATE users SET hash = :hash WHERE id = :userid",
                   hash=hash, userid=session["user_id"])
        
        flash("Password Changed Successfully")
        return redirect("/settings")

    else:
        return render_template("change_password.html", name=name)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)