import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # select user data
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # get current cash the user has
    cash = user[0]["cash"]

    # select rows of stocks the user has
    stocks = db.execute("SELECT * FROM stocks WHERE id = ?", user_id)

    # declare dictionaries for storing name of stock, prices of one share and total worth of particular stock for every stock the user has
    names = {}
    prices = {}
    totals = {}

    # initialise the total amount(cash + stocks'worth) to current cash
    total = cash

    # convert cash in dollar format
    cash = usd(cash)

    # for every stock, update the 3 dictionaries and increment the total amount
    for stock in stocks:
        values = lookup(stock["symbol"])
        name = values["name"]
        price = values["price"]
        symbol = values["symbol"]
        names[symbol] = name
        prices[symbol] = usd(price)
        totals[symbol] = stock["shares"] * price
        total += totals[symbol]

    # convert in dollar format
    for symbol in totals:
        totals[symbol] = usd(totals[symbol])
    total = usd(total)

    # display the stocks'data user has
    return render_template("index.html", stocks=stocks, names=names, prices=prices, totals=totals, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure symbol is entered
        if not request.form.get("symbol"):
            return apology("must provide symbol for the stock", 403)
        symbol = request.form.get("symbol")

        # Ensure the symbol is valid
        values = lookup(symbol)
        if values is None:
            return apology("Invalid symbol, try again!")

        # Ensure number of stocks is entered
        if not request.form.get("shares"):
            return apology("must provide number of stocks to be bought", 403)
        shares = request.form.get("shares")

        # Ensure the entered no of stocks is a positive integer
        try:
            shares = int(shares)
        except ValueError:
            return apology("The no of shares must be a positive integer. Try again")
        if shares <= 0:
            return apology("The no of shares must be a positive integer. Try again")

        # variables to be passes in sql commands
        symbol = symbol.upper()
        price = values["price"]
        name = values["name"]
        cost = shares * price
        user_id = session["user_id"]

        # get the current cash
        cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        # check if user has sufficient cash to complete the transaction
        if cost > cash[0]["cash"]:
            return apology("You don't have enough cash to make this transaction")

        # balance after transaction
        balance = cash[0]["cash"] - cost

        # record transaction details
        db.execute("INSERT INTO records(id, symbol, stock_name, shares, price, total_cost, balance, transacted, type) VALUES(?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'BOUGHT')",
                   user_id, symbol, name, shares, price, cost, balance)

        # update the cash the user has
        db.execute("UPDATE users SET cash = ?", balance)

        # no of shares before transaction
        total_shares = db.execute("SELECT * FROM stocks WHERE symbol = ? AND id = ?", symbol, user_id)

        # update no of shares after transaction
        # if he had some shares of the particular stock
        if len(total_shares) == 1:
            new_shares = total_shares[0]["shares"] + shares
            db.execute("UPDATE stocks SET shares = ? WHERE symbol = ? AND id = ?", new_shares, symbol, user_id)
        # if he didn't have any share of the stock before transaction, insert a row with data
        else:
            db.execute("INSERT INTO stocks(id, symbol, shares) VALUES(?, ?, ?)", user_id, symbol, shares)

        # redirect user to home page with a message that the transaction was successfull
        message = str(shares) + " share/s of " + name + " [" + symbol + "] bought successfully !"
        flash(message)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # get records of transactions
    user_id = session["user_id"]
    records = db.execute("SELECT * FROM records WHERE id = ?", user_id)

    # declare dictionaries for storing price and balance column values in records, in usd format
    prices = {}
    balances = {}

    # insert values in dictionaries in usd format
    for record in records:
        prices[record["transacted"]] = usd(record["price"])
        balances[record["transacted"]] = usd(record["balance"])

    # display every transaction the user has made in a table format with necessary details
    return render_template("history.html", records=records, prices=prices, balances=balances)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        values = lookup(request.form.get("symbol"))

        # if symbol is valid, show user the current price for the entered stock symbol
        if values is not None:
            name = values["name"]
            price = usd(values["price"])
            symbol = values["symbol"]
            return render_template("quoted.html", name=name, price=price, symbol=symbol)
        # if symbol is invalid
        else:
            return apology("Not found! Invalid Symbol")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username is entered
        if not request.form.get("username"):
            return apology("Username can't be blank")

        # Ensure entered username is available
        username = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(username) == 1:
            return apology("This username is not available")

        # Ensure password is entered
        if not request.form.get("password"):
            return apology("Please enter the password")

        # Ensure confirmation password is entered
        if not request.form.get("confirmation"):
            return apology("Please confirm the password")

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")

        # insert username and password hash into database
        password = request.form.get("password")
        db.execute("INSERT INTO users(username, hash) VALUES(?,?)", request.form.get("username"), generate_password_hash(password))

        # redirect to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure the symbol is selected
        if not request.form.get("symbol"):
            return apology("Please select the symbol of stocks you want to sell", 403)
        symbol = request.form.get("symbol")

        # Ensure the symbol is valid
        values = lookup(symbol)
        if values is None:
            return apology("Invalid symbol, try again!")

        # Ensure number of shares to be sold is entered
        if not request.form.get("shares"):
            return apology("must provide number of stocks to be sold", 403)
        shares = request.form.get("shares")

        # Ensure the entered no of shares is a positive integer
        try:
            shares = int(shares)
        except ValueError:
            return apology("The no of shares must be a positive integer. Try again")
        if shares <= 0:
            return apology("The no of shares must be a positive integer. Try again")

        # check if user owns the stocks for entered symbol
        avail_stock = db.execute("SELECT * FROM stocks WHERE id = ? AND symbol = ?", user_id, symbol)
        if len(avail_stock) != 1:
            return apology("You don't own any shares of " + symbol)

        # Ensure that the user owns the number of shares he is trying to sell
        if avail_stock[0]["shares"] < shares:
            return apology("You don't own " + str(shares) + " shares of " + symbol)

        # defining variables to pass in sql statements
        symbol = symbol.upper()
        price = values["price"]
        name = values["name"]
        cost = shares * price

        # Get the amount of cash the user has currently
        cash = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        # update balance
        balance = cash[0]["cash"] + cost

        # if remaining shares after transaction is 0, remove that stock from database, else update the shares
        new_shares = avail_stock[0]["shares"] - shares
        if new_shares == 0:
            db.execute("DELETE FROM stocks WHERE id = ? AND symbol = ?", user_id, symbol)
        else:
            db.execute("UPDATE stocks SET shares = ? WHERE id = ? AND symbol = ?", new_shares, user_id, symbol)

        # record the transaction details in database
        db.execute("INSERT INTO records(id, symbol, stock_name, shares, price, total_cost, balance, transacted, type) VALUES(?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'SOLD')",
                   user_id, symbol, name, shares, price, cost, balance)

        # update remaining cash the user has
        db.execute("UPDATE users SET cash = ?", balance)

        # redirect to index page with a message about successful transaction
        message = str(shares) + " share/s of " + name + " [" + symbol + "] sold successfully !"
        flash(message)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        stocks = db.execute("SELECT * FROM stocks WHERE id = ?", user_id)
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
