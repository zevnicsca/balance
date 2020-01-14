import os

import pymongo
from bson.objectid import ObjectId
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

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

# Configure PyMongo to use MongoDB
client = pymongo.MongoClient()
# Make the users collection
users = client.balance.users
# Make the groups  collection
groups = client.balance.groups

# If you need to deleate all the current entries in the datebase, un-comment the following two lines
# users.remove({})
# groups.remove({})

# A utility function to check if a username is in the database


def check_valid_user(username):
    rows = list(users.find({"username": username}))
    if len(rows) != 1:
        return False
    return True


@app.route("/")
@login_required
def index():
    """The homepage for a user once logged in"""

    # Get data on the logged in user (name and balances with freinds)
    current_user = list(users.find({"_id": ObjectId(session["user_id"])}))[0]
    current_username = current_user['username']
    balances = current_user['owes']
    # Get what groups the user belongs to
    user_groups = list(groups.find({"users": current_username}))
    # Pass the data to the template
    return render_template("index.html", user_groups=user_groups, current_username=current_username, balances=balances)


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
        rows = list(users.find({"username": request.form.get("username")}))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["_id"]

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Check is the username is ok to use
        if not request.form.get("username"):
            return apology("Missing Username")
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Enter and Confirm a Password")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Password and Confirmation must Match")

        rows = list(users.find({"username": request.form.get("username")}))

        if len(rows) > 0:
            return apology("Username Already Taken")

        # Insert the user into the db
        new_user = {
            "username": request.form.get("username"),
            "hash": generate_password_hash(request.form.get("password")),
            "owes": {}
        }
        id = users.insert_one(new_user).inserted_id

        # Log them in
        session["user_id"] = id
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    # Check if the username is in the db
    rows = list(users.find({"username": username}))
    # Respond accordingly
    if len(username) >= 1 and len(rows) == 0:
        return jsonify(True)
    return jsonify(False)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new group"""

    if request.method == "POST":
        # Get the data on the user creating the group
        current_user = list(users.find({"_id": session["user_id"]}))[0]
        users_list = [current_user['username']]
        for key in request.form:
            if "username" in key:
                if not check_valid_user(request.form[key]):
                    return apology("Invalid Username for Member")
                users_list.append(request.form[key])
        # Create the group and add it to the database
        new_group = [{
            "name": request.form.get("name"),
            "users": users_list,
            "expenses": []
        }]
        id = groups.insert_many(new_group)
        # Redirect the user back to homepage
        return redirect("/")
    else:
        return render_template("create.html")


@app.route("/groups")
@login_required
def group():
    """The page to view a given group"""

    # Get the group data
    group_id = ObjectId(request.args.get("id"))
    current_group = list(groups.find({"_id": group_id}))[0]

    # Pass it to the template
    return render_template("groups.html", group_page=True, group_id=group_id, group=current_group)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """ Create a New Expense"""

    if request.method == "POST":
        # Get the data on curent user
        current_username = list(users.find({"_id": session["user_id"]}))[0]['username']
        # Get the data on current group
        group_id = ObjectId(request.args.get("id"))
        current_group = list(groups.find({"_id": group_id}))[0]
        # Create the new expense with data from the from
        new_expense = {"name": request.form['name'],
                       "type": request.form['type'],
                       "description": request.form['description'],
                       "amount": float(request.form['amount']),
                       "payer": current_username}
        # Add the new expense to the group
        groups.update({"_id": group_id}, {"$set": {"expenses": [new_expense] + current_group["expenses"]}})
        # Get the users in the group
        group_users = list(set(current_group['users']) - set([current_username]))
        num_members = len(group_users) + 1
        # Loop through the users in the group
        for user in group_users:
            # Update the balance the current user share with that user
            users.update(
                {"username": current_username},
                {"$inc": {"owes."+user: float(request.form['amount'])/num_members}})
            # Update the balance that user shares with the current user
            users.update(
                {"username": user},
                {"$inc": {"owes."+current_username: - float(request.form['amount'])/num_members}})
        # Redirect back to the group page
        return redirect("/groups?id="+request.args.get("id"))
    else:
        return render_template("add.html", group_id=request.args.get("id"))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
