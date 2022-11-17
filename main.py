### MODULE IMPORTS ###
from tkinter import Menu
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from classes import * # import all classes from classes.py

'''
### POSTGRESQL CONFIG ###
db_host = 'satao.db.elephantsql.com'
db_name = 'jwwfjrox'
db_user = 'jwwfjrox'
db_pw = 'jQiFAyGF07Tghwk44c4GButvW2uKzsLi'
'''
### POSTGRESQL CONFIG ###
db_host = 'ec2-34-234-240-121.compute-1.amazonaws.com'
db_name = 'dcgsvhb0enfgfd'
db_user = 'ampoosmqdvdzte'
db_pw = '1494a152d2acffe248186b855286562322f43ab69a4ae0cd1b061bef24f36bf3'


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

            # redirect page to candidate, admin, voter
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

### VOTER PAGE ###
@app.route("/voter", methods=["GET", "POST"])
def voter():
    boundary = VoterPage()
    #name = VoterPage().controller.getName()
    if request.method == "GET":
        if "username" in session:
            return boundary.voterTemplate(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        print("12345")
        return boundary.buttonClicked(request.form)

### VOTER UPDATE ADDRESS PAGE ###
@app.route("/voterUpdateAddress", methods=["GET", "POST"])
def voterUpdateAddress():
    boundary = VoterPage()
    address_postalCode = VoterPage().controller.getAddress()
    if request.method == "GET":
        return boundary.voterTemplateUpdateAddress(session["username"], address_postalCode)

    elif request.method == "POST":
        test = boundary.controller.setAddress(request.form)
        return redirect(url_for("voter"))

'''
### LOGOUT (TO APPLY BCE) ###
@app.route("/logOut")
def logOut():
    boundary = Logout(session)
    session.clear()
    print(session)
    return boundary.logUserOut()
'''

@app.errorhandler(500)
def page_not_found(e):
    print(e)
    flash("Unauthorized!")
    return redirect(url_for("index"))


### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=80)
