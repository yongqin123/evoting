### MODULE IMPORTS ###
from tkinter import Menu
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from classes import * # import all classes from classes.py


### POSTGRESQL CONFIG ###
db_host = 'satao.db.elephantsql.com'
db_name = 'jwwfjrox'
db_user = 'jwwfjrox'
db_pw = 'jQiFAyGF07Tghwk44c4GButvW2uKzsLi'


### SESSION CONFIG (password & period) ###
app = Flask(__name__)
app.secret_key = "e_voting"
app.permanent_session_lifetime = timedelta(minutes=60)


### LOGIN PAGE ###
@app.route("/", methods=["GET", "POST"])
def index():
    boundary = LoginPage()
    if request.method == "GET":
        print("In get")
        return boundary.loginTemplate() # A-B

    elif request.method == "POST":
        print("inside POST of login")
        if boundary.controller.getCredentials(request.form): # B-C, C-E
            print("inside inside POST of login")
            # login success - add username & account_type in session
            session["username"] = request.form["username"]
            session["account_type"] = request.form["type"]

            # redirect page to candidate, super_admin, voter
            return LoginPage.redirectPage(session["account_type"]) # C-B

        else:
            flash(request.form["username"] + " login failed!")
            return boundary.loginTemplate() # redirect to login page


### CANDIDATE PAGE ###
@app.route("/candidate", methods=["GET", "POST"])
def candidate():
    boundary = CandidatePage()
    if request.method == "GET":
        if "username" in session:
            return boundary.candidateTemplate(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))
            
### LOGOUT (TO APPLY BCE) ###
@app.route("/logOut")
def logOut():
    boundary = Logout(session)
    session.clear()
    print(session)
    return boundary.logUserOut()


@app.errorhandler(500)
def page_not_found(e):
    flash("Unauthorized!")
    return redirect(url_for("index"))


### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0',port=80)
