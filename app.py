from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
from datetime import *
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, email_check, reg_mail, trans_mail, usd, lookup

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.jinja_env.filters["usd"] = usd

# Configure your MySQL database connection
config = {
    'user': 'root',
    'password': 'flaskrun',
    'host': 'localhost',
    'database': 'payify',
    'raise_on_warnings': True
}

def get_db_connection():
    conn = mysql.connector.connect(**config)
    return conn

def execute_query(query, query_params=None, fetch_results=True, commit_changes=False):
    results = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Add the dictionary=True parameter

        if query_params is not None:
            cursor.execute(query, tuple(query_params))
        else:
            cursor.execute(query)

        if fetch_results:
            results = cursor.fetchall()

        if commit_changes:
            conn.commit()
    except mysql.connector.Error as e:
        print(f"Error executing query: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return results

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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
    """user's Dashboard"""
    # Query for user's cash
    user = execute_query("SELECT first_name, last_name, balance FROM user WHERE user_id = %s", (session["user_id"],))
    assets = execute_query("SELECT stock_symbol, total_quantity FROM stockAsset WHERE user_id = %s AND total_quantity != 0", (session['user_id'],))
    stock_value = 0
    # Iterate over assets list
    for asset in assets:
        # Lookup for Stock Name and Current Price using user's Stock Symbol
        quote = lookup(asset["stock_symbol"])
        asset["stock_symbol"] = asset["stock_symbol"].upper()
        asset["name"] = quote["name"]
        asset["price"] = float(quote["price"])
        asset["value"] = asset["price"] * asset["total_quantity"]
        stock_value += asset["value"]
        
    # Query for user's cash
    cash = execute_query("SELECT balance FROM user WHERE user_id = %s", (session['user_id'],))
    total = stock_value + float(cash[0]["balance"])
    # Get user's First and last name for Navbar and user's cash for balance
    
    # Query for user's recent activity
    trans1 = execute_query("SELECT u.first_name, u.last_name, t.datetime, t.transaction_type, t.amount, t.transaction_id "
                            "FROM transaction AS t "
                            "INNER JOIN user AS u ON t.receiver_id = u.user_id "
                            "WHERE t.sender_id = %s", (session["user_id"],))
    trans = trans1[::-1]

    return render_template("index.html", user=user, trans=trans, total=usd(total), stock_value=usd(stock_value), cash=usd(cash[0]["balance"]))

@app.route("/portfolio")
@login_required
def portfolio():
    """Show portfolio of stocks"""
    # Query database for user's stock assets
    assets = execute_query("SELECT stock_symbol, total_quantity FROM stockAsset WHERE user_id = %s AND total_quantity != 0", (session['user_id'],))


    stock_value = 0
    # Iterate over assets list
    for asset in assets:
        # Lookup for Stock Name and Current Price using user's Stock Symbol
        quote = lookup(asset["stock_symbol"])
        asset["stock_symbol"] = asset["stock_symbol"].upper()
        asset["name"] = quote["name"]
        asset["price"] = float(quote["price"])
        asset["value"] = asset["price"] * asset["total_quantity"]
        stock_value += asset["value"]

    # Query for user's cash
    cash = execute_query("SELECT balance FROM user WHERE user_id = %s", (session['user_id'],))
    total = stock_value + float(cash[0]["balance"])

    return render_template("portfolio.html", rows=assets, cash=usd(cash[0]["balance"]), total=usd(total), stock_value=usd(stock_value))

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
        rows = execute_query("SELECT * FROM user WHERE email = %s", (request.form.get("email").lower(),))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("invalid username and/or password")
            classs = "alert-danger"
            return render_template("login.html", classs=classs)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        date_of_birth_str = request.form.get('date_of_birth')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not first_name:
            return apology('Missing first name', 403)
        if not last_name:
            return apology('Missing last name', 403)
        if not email:
            return apology('Missing Email', 403)
        if not date_of_birth_str:
            return apology('Missing Date of birth', 403)
        if not password:
            return apology('Missing Password', 403)
        if password != confirm_password:
            flash("Passwords don't match")
            return render_template("signup.html", classs="alert-danger")
        
        dob = datetime.strptime(date_of_birth_str, "%Y-%m-%d")
        age = (datetime.now() - dob) // timedelta(days=365.25)
        if age < 18:
            flash("You must be at least 18 years old.")
            return render_template('signup.html', classs="alert-danger")

        # Check Email is valid
        email = email.lower()
        if not email_check(email):
            flash('Invalid email address')
            return render_template('signup.html', classs="alert-danger")

        # Ensure email isn't already exists
        user = execute_query('SELECT * FROM user WHERE email = %s', (email,))
        if user:
            flash('Email address already taken')
            return render_template('signup.html', classs="alert-danger")

        # Encrypt user's password
        hashed_password = generate_password_hash(request.form.get("password"))

        # Insert user's inputs into DataBase
        execute_query(
            'INSERT INTO payify.user (email, password, first_name, last_name, date_of_birth, balance) VALUES (%s, %s, %s, %s, %s, %s)',
            (email, hashed_password, first_name, last_name, dob.date(), 5000), fetch_results=False, commit_changes=True
        )

        user = execute_query('SELECT * FROM user WHERE email = %s', (email,))
        print(user)
        session['user_id'] = user[0]["user_id"]
        reg_mail(email, first_name) 
        flash('Welcome!')
        return redirect('dashboard')
    else:
        return render_template('signup.html')

@app.route("/transfer", methods=['GET', 'POST'])
@login_required
def transfer():
    """transfer money"""
    user = execute_query("SELECT first_name, last_name, email, balance FROM user WHERE user_id = %s", (session["user_id"],))

    if request.method == "POST":
        if not request.form.get("email"):
            return apology("Missing Email", 400)
        
        if not request.form.get("cash"):
            return apology("missing amount of cash", 400)
        
        else:
            cash_amount = float(request.form.get("cash"))
            email = request.form.get("email").lower()

        if not email_check(email):
            flash("Email isn't valid")
            return render_template("transfer.html", classs="alert-danger", user=user)
        
        if cash_amount > user[0]["balance"]:
            flash("You cannot afford")
            return render_template("transfer.html", classs="alert-danger", user=user)

        # Ensure email isn't users's one
        if request.form.get("email") == user[0]['email']:
            flash("You can't send to yourself")
            return render_template("transfer.html", classs="alert-danger", user=user)

        # Ensure the email is exists
        receiver = execute_query("SELECT * FROM user WHERE email = %s", (email,))
        if not receiver:
            flash("Email isn't exists")
            return render_template("transfer.html", classs="alert-danger", user=user)
        
        # if the inputed email is exsist and valid get his user id in user2id variable
        else:
            receiver_id = receiver[0]["user_id"]

        now = datetime.now()

        fee = round(cash_amount * 0.01, 2)
        net_amount = cash_amount - fee

        # Update user's amount of cash (sender)
        execute_query("UPDATE user SET balance = balance - %s WHERE user_id = %s", (cash_amount, session["user_id"]), fetch_results=False, commit_changes=True)

        # Update user's amount of cash (receiver)
        execute_query("UPDATE user SET balance = balance + %s WHERE user_id = %s", (net_amount, receiver_id), fetch_results=False, commit_changes=True)

        # Insert transaction to the database part1 (sender side)
        execute_query("INSERT INTO Transaction (sender_id, receiver_id, amount, datetime, transaction_type) VALUES (%s, %s, %s, %s, 'sent')",
                   (session["user_id"], receiver_id, -cash_amount, now), fetch_results=False, commit_changes=True)
        
        # Insert transaction to the database part1 (receiver side)
        execute_query("INSERT INTO Transaction (sender_id, receiver_id, amount, datetime, transaction_type) VALUES (%s, %s, %s, %s, 'received')",
                   (receiver_id, session["user_id"], cash_amount, now), fetch_results=False, commit_changes=True)

                # Get mail (reciver side) details
        
        # Get mail (sender side) details
        sender_mail = user[0]['email']
        reciver_details = {'first_name': receiver[0]["first_name"], 'last_name': receiver[0]["last_name"], 'email': email}
        trans_sender = {'amount': '%.2f' % float(cash_amount), 'fee': '%.2f' % float(fee), 'net_amount': '%.2f' % float(net_amount), 'datetime': now, 'type': 'sent', 'type2': 'to','transaction_type': 'sent',
                        'subject': "Your payment has completed", 'header': "received from"}
        trans_mail(sender_mail, reciver_details, trans_sender)

        reciver_mail = email
        sender_details = {'first_name': user[0]["first_name"], 'last_name': user[0]["last_name"], 'email': user[0]['email']}
        trans_reciver = {'amount': '%.2f' % float(cash_amount), 'fee': '%.2f' % float(fee), 'net_amount': '%.2f' % float(net_amount), 'datetime': now, 'type': 'received', 'type2': 'from', 'transaction_type': 'received',
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
    user = execute_query("SELECT first_name, last_name FROM user WHERE user_id = %s", (session["user_id"],))
    
    # Query for user's recent activity
    trans1 = execute_query("SELECT u.first_name, u.last_name, t.datetime, t.transaction_type, t.amount, t.transaction_id "
                            "FROM transaction AS t "
                            "INNER JOIN user AS u ON t.receiver_id = u.user_id "
                            "WHERE t.sender_id = %s", (session["user_id"],))
    trans = trans1[::-1]

    return render_template("transactions.html", user=user, trans=trans)

@app.route("/payment", methods=["GET"])
@login_required
def payment():
    """Payment Details Page"""

    #Get user's First and last name for Navbar
    name = execute_query("SELECT first_name, last_name FROM user WHERE user_id = %s", (session["user_id"],))

    # Get transaction or payment id from args
    payment_id = request.args.get('id')
    
    # Check that if args doesn't include payment id
    if not request.args.get('id'):
        return apology('Not found', 404)

    # Query DataBase for transactions Details
    details = execute_query("SELECT * FROM transaction INNER JOIN user ON transaction.receiver_id = user.user_id WHERE transaction_id = %s"
                         , (payment_id,))

    details[0]["amount"] = float(details[0]["amount"])
    details[0]["fee"] = round(details[0]["amount"] * 0.01, 2)
    details[0]["net_amount"] = details[0]["amount"] - details[0]["fee"]

    return render_template("payment.html", name=name, details=details)

@app.route("/settings")
@login_required
def settings():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = execute_query("SELECT first_name, last_name, email FROM user WHERE user_id = %s", (session["user_id"],))

    if request.method == "POST":

        return render_template("settings.html")

    else:
        return render_template("settings.html", name=name)

@app.route("/settings/name", methods=["GET", "POST"])
@login_required
def name():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = execute_query("SELECT first_name, last_name FROM user WHERE user_id = %s", (session["user_id"],))

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
        rows = execute_query("SELECT password FROM user WHERE user_id = %s", (session["user_id"],))

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("invalid current password")
            return render_template("change_name.html", classs="alert-danger", name=name)

        # update user's first, last name
        execute_query("UPDATE user SET first_name = %s, last_name = %s WHERE user_id = %s", (request.form.get("first_name"), request.form.get("last_name"), session["user_id"]), fetch_results=False, commit_changes=True)
        
        flash("Name Changed Successfully")
        return redirect("/settings")

    else:
        return render_template("change_name.html", name=name)

@app.route("/settings/email", methods=["GET", "POST"])
@login_required
def email():
    """Account Settings Page"""

    #Get user's info for Navbar and settings
    name = execute_query("SELECT first_name, last_name, email FROM user WHERE user_id = %s", (session["user_id"],))

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
        result = execute_query("SELECT email FROM user WHERE email = %s",
                            (email,))

        if len(result) == 1:
            flash("Email Address isn't avaliable")
            classs = "alert-danger"
            return render_template("change_email.html", classs=classs, name=name)
        
        # Query Database for user's hash
        rows = execute_query("SELECT password FROM user WHERE user_id = %s",
                          (session["user_id"],))

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["password"], request.form.get("password")):
            flash("invalid current password")
            classs = "alert-danger"
            return render_template("change_email.html", classs=classs, name=name)
            # update user's Email
        execute_query("UPDATE user SET email = %s WHERE user_id = %s",
                (email, session["user_id"]), fetch_results=False, commit_changes=True)
        
        flash("Email Changed Successfully")
        return redirect("/settings")

    else:
        return render_template("change_email.html", name=name)
    
@app.route("/settings/password", methods=["GET", "POST"])
@login_required
def password():
    """Account Settings Page"""
    #Get user's info for Navbar and settings
    name = execute_query("SELECT first_name, last_name FROM user WHERE user_id = %s", (session["user_id"],))

    if request.method == "POST":
        current_password = request.form.get("old_password")
        new_password = request.form.get("password")
        confirm_new_password = request.form.get("confirm_password")
        # Ensure old password isn't blank
        if not current_password:
            return apology("missing old password")

        if not new_password:
            return apology("missing password")

        # Ensure passwords are match
        if new_password != confirm_new_password:
            flash("Passwords don't match")
            return render_template("change_password.html", classs="alert-danger", name=name)

        # Query Database for user's hash
        rows = execute_query("SELECT password FROM user WHERE user_id = %s", (session["user_id"],))

        # Check inputed Password with user's one
        if not check_password_hash(rows[0]["password"], request.form.get("old_password")):
            flash("invalid current password")
            classs = "alert-danger"
            return render_template("change_password.html", classs=classs, name=name)

        # Encrypt user's password
        hash = generate_password_hash(request.form.get("password"))

        # update user's password
        execute_query("UPDATE user SET password = %s WHERE user_id = %s",
                (hash, session["user_id"]),fetch_results=False, commit_changes=True)
        
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



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        quantity = request.form.get("shares")
        if not symbol:
            return apology("missing symbol", 400)
        if not quantity:
            return apology("missing shares", 400)
        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("invalid symbol", 400)

        # Get the current Time
        time = datetime.now()

        # Declare a variable for the final price
        final_price = float(quote["price"]) * int(request.form.get("shares"))

        # Query for user's cash
        cash = execute_query("SELECT balance FROM user WHERE user_id = %s", (session['user_id'],))[0]["balance"]

        # Ensure if user can't afford stock price
        if cash < final_price:
            return apology("can't afford", 400)
        
        # Insert stock trade into Database
        execute_query("INSERT INTO StockTrade (user_id, stock_symbol, purchase_price, quantity, datetime) VALUES (%s, %s, %s, %s, %s)",
                      (session['user_id'], symbol, quote["price"], quantity, time), fetch_results=False, commit_changes=True)

        # Update user's stock asset
        stock_asset = execute_query("SELECT * FROM StockAsset WHERE user_id = %s AND stock_symbol = %s", (session['user_id'], symbol))
        if not stock_asset:
            execute_query("INSERT INTO StockAsset (user_id, stock_symbol, total_quantity) VALUES (%s, %s, %s)", (session['user_id'], symbol, quantity), fetch_results=False, commit_changes=True)
        else:
            execute_query("UPDATE StockAsset SET total_quantity = total_quantity + %s WHERE user_id = %s AND stock_symbol = %s", (quantity, session['user_id'], symbol), fetch_results=False, commit_changes=True)

        # Update user amount of cash
        execute_query("UPDATE user SET balance = balance - %s WHERE user_id = %s", (final_price, session["user_id"]), fetch_results=False, commit_changes=True)

        flash('Bought!')
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("buy.html")
    
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Query DataBase for user's Stocks and Amount of Shares 
    rows = execute_query("SELECT stock_symbol, purchase_price, quantity, datetime FROM stockTrade WHERE user_id = %s", (session["user_id"],))

    trans = rows[::-1]
    return render_template("history.html", rows=trans)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # Query DataBase for user's Stocks
    rows = execute_query("SELECT stock_symbol, total_quantity FROM stockAsset WHERE user_id = %s AND total_quantity != 0", (session["user_id"],))
    if request.method == "POST":

        # Ensure symbol is selected
        if not request.form.get("symbol"):
            return apology("missing symbol", 400)

        # Ensure shares isn't blank
        if not request.form.get("shares"):
            return apology("missing shares", 400)

        # Get user inputs
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Query DataBase for user's Shares
        user_shares = execute_query("SELECT total_quantity FROM StockAsset WHERE user_id = %s AND stock_symbol = %s", (session["user_id"], symbol))[0]["total_quantity"]

        # Ensure input shares is available
        if int(shares) > user_shares:
            return apology("too many shares", 400)

        # Lookup for stock price
        quote = lookup(symbol)
        price = quote["price"]
        final_price = float(price) * int(shares)

        # Get the current Time
        now = datetime.now()

        # Insert transaction infos into Database
        execute_query("INSERT INTO StockTrade (user_id, stock_symbol, purchase_price, quantity, datetime) VALUES (%s, %s, %s, %s, %s)",
                      (session["user_id"], symbol, price, -int(shares), now), fetch_results=False, commit_changes=True)

        # Update user amount of cash
        execute_query("UPDATE StockAsset SET total_quantity = total_quantity - %s WHERE user_id = %s AND stock_symbol = %s", (int(shares), session['user_id'], symbol), fetch_results=False, commit_changes=True)

        execute_query("UPDATE user SET balance = balance + %s WHERE user_id = %s", (final_price, session["user_id"]), fetch_results=False, commit_changes=True)

        flash("Sold!")
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("sell.html", rows=rows)
