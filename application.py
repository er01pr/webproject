from __future__ import print_function
import sys

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from datetime import datetime



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
#Get the current data of the stock.

    #SUM all similar stock values from Portfolio.
    ports = db.execute("SELECT *, SUM(quantity) as sharetotal FROM portfolio WHERE id = :id GROUP BY name", id=session["user_id"])

    #Get the remaining cash of the user from the users table.
    get_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])

    #Convert the get_cash dict to float so it can be displayed to index.html
    remaining_cash = get_cash[0]['cash']

    #SUM the stocks' total value plus the remaining cash.
    get_grand_total = db.execute("SELECT *, SUM(total) as grand_total FROM portfolio where id = :id", id=session["user_id"])
    grand_total_fl = get_grand_total[0]['grand_total']

    #Compute the Profit/Loss = Price Today - Bought Price / Price Today


    #Hold value is the sum of the shares * price of each shares in the portfolios PLUS the remaining cash.
    if grand_total_fl != None:
        hold_value = grand_total_fl + remaining_cash
        #Update hte current hold value of the user
        db.execute("UPDATE users SET hold_value = :hold_value WHERE id = :id", id=session["user_id"], hold_value=hold_value)
    else:
        hold_value = remaining_cash


    return render_template("index.html", ports=ports, remaining_cash = remaining_cash, hold_value=hold_value,)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        #Access the form data
        symbol = request.form.get("symbol")

        #Check if the shares was an integer
        try:
            quantity = int(request.form.get("shares"))
        except:
            return apology ("Please enter a whole number", 400)


        if int(quantity) < 0:
            return apology ("Please enter a positive value", 400)

        #Lookup the stock symbol data (price, symbol, company name)
        stock = lookup(symbol)

        if not symbol:
            return apology ("Invalid ticker symbol", 400)

        if not stock:
            return apology ("Invalid ticker symbol", 400)

        stock_price = stock['price']

        #Get the current percent change of the stock
        changePercent = stock['changePercent']

        #Created a new table using CREATE TABLE 'portfolio' ('user' text, 'quantity' integer, 'price' numeric(15, 2), 'symbol' text)

        #Get the total cash value of the user from the database
        get_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])

        #Convert the get_cash dict to float
        check_cash = float(get_cash[0]['cash'])

        #Get the current date and time
        now = datetime.now()

        date_time = now.strftime("%d/%m/%Y %H:%M:%S")

        if not stock:
            return apology ("Please enter a valid stock", 403)

        #Compute the total amount of the shares bought (One company stock only)
        total = stock_price * float(quantity)

        if total > check_cash:
            return apology("Not enough cash", 403)

        #Check if the cash on hand is enough to purchase the order.
        if check_cash > total:
            #Update the total amount of cash in hand by subtracting the ordered stocks.
            db.execute("UPDATE users SET cash = cash - :total WHERE id = :id", id=session["user_id"], total=total)


        #Check if the total cash is enough for the stock purchase.
        if total < check_cash:
            #Query if the stock symbol is already in the portfolio.
            rows = db.execute("SELECT * FROM portfolio WHERE symbol = :symbol AND id = :id", id=session["user_id"], symbol=symbol)

            #Add the stock in the history table
            history = db.execute("INSERT INTO history (symbol, quantity, price, transacted, id) VALUES (?, ?, ?, ?, ?)", symbol, int(quantity), float(stock_price), date_time, session["user_id"] )

            #If the stock already exists in the portfolio. Update the quantity.
            if len(rows) == 1:
                db.execute("UPDATE portfolio SET quantity = quantity + :quantity AND total = :total AND stock_price = :stock_price WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol, quantity=quantity, total=total, stock_price = float(stock_price))
            else:
                #Insert the user, shares bought, shares price, and the quantity bought in portfolio table.
                db.execute("INSERT INTO portfolio (quantity, total, symbol, id, stock_price, name, percent_change) VALUES (?, ?, ?, ?, ?, ?, ?)", int(quantity), total, symbol, session['user_id'], float(stock_price), stock['name'], changePercent)


    return redirect (url_for('index'))

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    #Get the current data of the stock.

    #SUM all similar stock values from Portfolio.
    ports = db.execute("SELECT * FROM history WHERE id = :id", id=session["user_id"])

    #Get the remaining cash of the user from the users table.
    get_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])

    #Convert the get_cash dict to float so it can be displayed to index.html
    remaining_cash = get_cash[0]['cash']

    #SUM the stocks' total value plus the remaining cash.
    get_grand_total = db.execute("SELECT *, SUM(total) as grand_total FROM portfolio where id = :id", id=session["user_id"])
    grand_total_fl = get_grand_total[0]['grand_total']



    return render_template("history.html", ports=ports)


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

    #Access the form data
    symbol = request.form.get("symbol")

    #Render the quote.html page
    if request.method == "GET":
        return render_template("quote.html")

    #Lookup the stock info
    if request.method == "POST":
        stock = lookup(symbol)
        if stock != None:
            return render_template("quoted.html", stock=stock)
        else:
            return apology ("Invalid ticker symbol", 400)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        #Redirect the user to the registration form.
        return render_template("register.html")
    if request.method == "POST":
        #Access Form Data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #Check if the user entered an input
        if not username:
            return apology("Please enter a username", 400)
        if not password:
            return apology("Please enter a password", 400)
        if not confirmation:
            return apology("Please enter a password confirmation", 400)

        #Check if the username that was entered is already registered.
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        #If the number of row is 1 then a user is already registered using the entered username.
        if len(rows) == 1:
            return apology ("The user is already registered. Please log-in instead", 400)


        #Check if the password and the confirmation password is the same.
        if password==confirmation:
            hashpw = generate_password_hash(password)
        else:
            return apology("Password doesn't match", 400)

        #Check if the hash that is generated have an equivalent password in the database.
        if check_password_hash(hashpw, password)==True:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashpw)
        else:
            return apology ("Hash doesn't match", 400)

        return redirect ("/")

    #return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "GET":

        #Query for all the stocks in posession.
        ports = db.execute("SELECT *, SUM(quantity) as sharetotal FROM portfolio WHERE id = :id GROUP BY name", id=session["user_id"])

        return render_template("sell.html", ports=ports)
    if request.method == "POST":
        #Access the form data
        symbol = request.form.get("symbol")

        #Check if the shares was an integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology ("Please enter a whole number", 400)

        #Query for the total quantity of that stock in posession
        get_quantity = db.execute("SELECT quantity FROM portfolio WHERE id = :id AND symbol = :symbol", id=session['user_id'], symbol=symbol)
        #Convert the quantity dict to int
        get_quantity_int = int(get_quantity[0]['quantity'])

        #Check if the user input a positive number.
        if shares < 0:
            return apology ("Please enter a positive value", 403)

        #Get the current date and time
        now = datetime.now()

        date_time = now.strftime("%d/%m/%Y %H:%M:%S")

        if shares < 0:
            return apology ("Please enter a positive value", 403)
        #Lookup the stock symbol data (price, symbol, company name)
        if shares > get_quantity_int:
            return apology ("Selling more than you own?", 400)
        stock = lookup(symbol)

        stock_price = stock['price']

        #Created a new table using CREATE TABLE 'portfolio' ('user' text, 'quantity' integer, 'price' numeric(15, 2), 'symbol' text)

        #Get the total cash value of the user from the database
        get_cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])

        #Convert the get_cash dict to float
        check_cash = float(get_cash[0]['cash'])

        if not stock:
            return apology ("Please enter a valid stock", 403)

        #Compute the total amount of the shares bought (One company stock only)
        total = stock_price * float(shares)

        #Update the total amount of cash in hand by adding the sold stocks.
        db.execute("UPDATE users SET cash = cash + :total WHERE id = :id", id=session["user_id"], total=total)

        #Check if the total quantity of shares is equal to the quantity the user is trying to sell.


        #Add the stock in the history table
        history = db.execute("INSERT INTO history (symbol, quantity, price, transacted, id) VALUES (?, ?, ?, ?, ?)", symbol, int(shares) * -1, float(stock_price), date_time, session["user_id"] )

        #If it's equal then delete the stock in the portfolio. #Else, Update the quantity of that stock in the portfolio.
        if shares == get_quantity_int:
            db.execute("DELETE FROM portfolio WHERE id = :id AND symbol = :symbol", id=session['user_id'], symbol=symbol)
        else:
            db.execute("UPDATE portfolio SET quantity = quantity - :shares WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol=symbol, shares=shares)

        return redirect (url_for('index'))


@app.route("/rankings", methods=["GET", "POST"])
@login_required
def rankings():

    if request.method == "GET":

        return render_template("rankings.html")
    if request.method == "POST":

        #Show leaderboards in terms of hold value, change in hold value, and number of transactions per day, week, month and year

        #Access form data
        holdvalue = request.form.get("holdvalue")
        percent_change = request.form.get("change")
        transactions = request.form.get("transactions")

        day = request.form.get("day")
        week = request.form.get("week")
        month = request.form.get("month")
        year = request.form.get("year")

        #Compute the percent Change

        #Query all stocks of a user and add all of the percent change.
        #user_percentchange = db.execute("SELECT ")

        #Compute the Hold Value
        users = db.execute ("SELECT *, history.id, COUNT(transacted) AS transactions, users.username, users.hold_value FROM history INNER JOIN users ON history.id = users.id GROUP BY history.id ORDER BY COUNT(transacted) DESC")

        #Percent change
        ports = db.execuute("SELECT portfolio.id, SUM(percent_change) AS sum_percent FROM portfolio GROUP BY id ORDER BY SUM(percent_change) ASC")


        return render_template("rankings.html", users=users, ports=ports)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
