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


### PARTY PAGE ###
@app.route("/party", methods=["GET", "POST"])
def party():
    boundary = PartyPage()
    if request.method == "GET":
        if "username" in session:
            return boundary.partyTemplate(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))
    elif request.method == "POST":
        return boundary.buttonClicked(request.form)

@app.route("/Party/CreateProfile", methods=["GET", "POST"])
def CreateProfile():
    boundary = PartyPage()
    partyName = session["username"]
    if request.method == "GET":
        return boundary.partyTemplateCreate()

    elif request.method == "POST":

        error, result =  boundary.controller.createProfile(request.form, request.form.getlist)

        if result:
            flash("Profile successfully created!")
            return boundary.partyTemplate(session["username"])

        else:
            print(f"In main result : {error}")
            flash(error)
            return boundary.partyTemplateCreate() 

    
@app.route("/Party/UpdateProfile", methods=["GET", "POST"])
def UpdateProfile():
    boundary = PartyPage()
    partyName = session["username"]
    if request.method == "GET":
        if "username" in session:
            return boundary.partyGetDistrict()
            

        elif request.method == "POST":
            boundary.controller.updateProfile(request.form, partyName)
            #return boundary.partyTemplateUpdate(partyName)

    """  elif request.method == "POST":

        error, result =  boundary.controller.createProfile(request.form, request.form.getlist)

        if result:
            flash("Profile successfully created!")
            return redirect(url_for("party"))

        else:
            print(f"In main result : {error}")
            flash(error)
            return redirect(url_for("CreateProfile")) """

### VOTER PAGE ###
@app.route("/voter", methods=["GET", "POST"])
def voter():
    boundary = VoterPage()
    #name = VoterPage().controller.getName()
    if request.method == "GET":
        if "username" in session:
            details = VoterPage().controller.getDetails()
            constituency = VoterPage().controller.getDistrictName()
            return boundary.voterTemplate(session["username"], details, constituency)
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
    if request.method == "GET":
        return boundary.voterTemplateUpdateAddress(session["username"])

    elif request.method == "POST":
        boundary.controller.setAddress(request.form)
        return redirect(url_for("voter"))

### VOTER UPDATE ADDRESS PAGE ###
@app.route("/voterUpdatePhoneNumber", methods=["GET", "POST"])
def voterUpdatePhoneNumber():
    boundary = VoterPage()
    if request.method == "GET":
        return boundary.voterTemplateUpdatePhoneNumber(session["username"])

    elif request.method == "POST":
        boundary.controller.setPhoneNumber(request.form)
        return redirect(url_for("voter"))

@app.route("/voterViewParties", methods=["GET", "POST"])
def voterViewParties():
    boundary = VoterPage()
    parties = VoterPage().controller.getParties()
    if request.method == "GET":
        return boundary.voterTemplateViewParties(session["username"], parties)
    
    elif request.method == "POST":
        session["candidates"] = VoterPage().controller.getCandidatesByDistrict(request.form)
        print(session["candidates"])
        return redirect(url_for("voterViewCandidates"))

@app.route("/voterViewCandidates", methods=["GET", "POST"])
def voterViewCandidates():
    boundary = VoterPage()
    parties = VoterPage().controller.getParties()
    
    if request.method == "GET":
        return boundary.voterTemplateViewCandidates(session["username"], parties, session["candidates"])
    
    elif request.method == "POST":
        session["candidates"] = VoterPage().controller.getCandidatesByDistrict(request.form)
        return redirect(url_for("voterViewCandidates"))

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
