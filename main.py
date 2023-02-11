### MODULE IMPORTS ###

from tkinter import Menu
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from werkzeug.utils import secure_filename
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
            
            if request.form["type"] == "party":
                session["party"] = request.form["party"]

            # redirect page to candidate, admin, voter
            return LoginPage.redirectPage(session["account_type"]) # C-B

        else:
            flash(request.form["username"] + " login failed!")
            return boundary.loginTemplate() # redirect to login page


### PARTY PAGE ###
@app.route("/party", methods=["GET", "POST"])
def party():
    boundary = PartyPage()
    partyDetails = PartyPage().controller.getPartyDetails()
    print(partyDetails)
    if "username" in session:
        if request.method == "GET":
            return boundary.partyTemplate(session["username"], session["party"], partyDetails)
        elif request.method == "POST":
            #print("partypost")
            return boundary.buttonClicked(request.form)
    else:
        flash("login first!")
        return redirect(url_for("index"))


@app.route("/CreatePartyProfile", methods=["GET", "POST"])
def CreatePartyProfile():
    boundary = PartyPage()
    if "username" in session:
        if request.method == "GET":
            if boundary.controller.ProfileExists(session["party"]) == True:
                #print("access denied")
                flash("Party profile already exists!")
                return redirect(url_for("party"))

            else:
                #print("access allowed")
                return boundary.partyTemplateProfileCreate(session["party"]) #manage to enter 

    
        elif request.method == "POST":
            boundary.controller.createPartyProfile(request.form, request.files)
            flash("Party profile successfully created!")
            return redirect(url_for("party"))
    else:
        flash("login first!")
        return redirect(url_for("index"))


@app.route("/updatePartyProfile", methods=["GET", "POST"])
def UpdatePartyProfile():
    boundary = PartyPage()
    if "username" in session:
        if request.method == "GET":
            
            if boundary.controller.ProfileExists(session["party"]):
                return boundary.updatePartyTemplate(session["party"])
            
            else:
                flash("Create a party profile first!")
                return redirect(url_for("party"))
        
        elif request.method == "POST":
            boundary.controller.updatePartyProfile(request.form, request.files, session["party"])
            flash("Party profile successfully updated!")
            return redirect(url_for("party"))
    else:
        flash("login first!")
        return redirect(url_for("index"))

@app.route("/Party/DistrictCreateProfile", methods=["GET", "POST"])
def CreateDistrictProfile():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
            partyProfile_exists = boundary.controller.ProfileExists(session["party"])
            if partyProfile_exists == True:
                contestingZones = boundary.controller.getContestingZones()
                data = boundary.controller.getAll(session["party"])
                print(data)
                return boundary.partyDistrictTemplateCreate(session["party"], data , contestingZones)
            else:
                flash("Create a party profile first!")
                return redirect(url_for("party"))

        elif request.method == "POST":
            print(request.form["button_type"])
            button = request.form["button_type"]

            if len(button) > 2:
                if button.split("_")[1] == "remove":
                    session["districtName"] = request.form["button_type"].split("_")[0]
                    boundary.controller.delete(session["party"], session["districtName"])
                    return redirect(url_for("CreateDistrictProfile"))
                else:
                    return boundary.buttonClicked(request.form)
            else:
                return boundary.buttonClicked(request.form)

    else:
        flash("login first!")
        return redirect(url_for("index"))



####################################################

@app.route("/Party/DistrictCreateProfile/test", methods=["GET", "POST"])
def Test():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
           
            contestingZones = boundary.controller.getContestingZones()
            data = boundary.controller.getAll(session["party"])
            print("hereeeeee")
            print(f'zones : {contestingZones}')
            
            return boundary.partyDistrictTemplateModal(session["party"], data, contestingZones)
            

        elif request.method == "POST":
           
            #partyDistrictProfile_exists = boundary.controller.DistrictExists(request.form, session["party"])

            
            error, result =  boundary.controller.createDistrictProfile(request.form, request.form.getlist, request.files.getlist)
            if result:
                flash("Profile successfully created!")
                contestingZones = boundary.controller.getContestingZones()
                data = boundary.controller.getAll(session["party"]) #get all candidate's data
                return redirect(url_for("CreateDistrictProfile"))

            else:
                print(f"In main result : {error}")
                flash(error)
                contestingZones = boundary.controller.getContestingZones()
                data = boundary.controller.getAll(session["party"])
                return boundary.partyDistrictTemplateCreate(session["party"], data , contestingZones)
           
       
    else:
        flash("login first!")
        return redirect(url_for("index"))

####################################################

""" @app.route("/Party/DistrictCreateProfile/edit", methods=["GET", "POST"])
def Edit():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
           
            data = boundary.controller.getCandidatesByDistrict(session["party"])
            print("hereeeeee")
            print(f'zones : {data}')
            
            return boundary.partyEditDistrictTemplateModal(data)
            

        elif request.method == "POST":
           
            #partyDistrictProfile_exists = boundary.controller.DistrictExists(request.form, session["party"])
            error, result = boundary.controller.updateDistrict(request.files.getlist, request.form.getlist)
            if result:
                flash("District profile successfully updated!")
                return redirect(url_for("CreateDistrictProfile"))
            else:
                flash(error)
                return redirect(url_for("CreateDistrictProfile"))
            
       
    else:
        flash("login first!")
        return redirect(url_for("index")) """

@app.route("/Party/DistrictCreateProfile/edit", methods=["GET", "POST"])
def Edit():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
           
            data = boundary.controller.getCandidatesByDistrict(session["party"])
            print("hereeeeee editing")
            print(f'########candidates : {data}')
            
            return boundary.partyDistrictTemplateUpdate(data)
            

        elif request.method == "POST":
           
            #partyDistrictProfile_exists = boundary.controller.DistrictExists(request.form, session["party"])
            error, result = boundary.controller.updateDistrict(request.files.getlist, request.form.getlist)
            if result:
                flash("District profile successfully updated!")
                return redirect(url_for("CreateDistrictProfile"))
            else:
                flash(error)
                return redirect(url_for("CreateDistrictProfile"))
            
       
    else:
        flash("login first!")
        return redirect(url_for("index"))



""" @app.route("/Party/addingDistrict", methods=["GET", "POST"])
def AddDistrict():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
            partyProfile_exists = boundary.controller.ProfileExists(session["party"])
            if partyProfile_exists == True:
                contestingZones = boundary.controller.getContestingZones()
                data = boundary.controller.getAll(session["party"])
                print(data)
                return boundary.partyDistrictTemplateModal(session["party"], data , contestingZones)
            else:
                flash("Create a party profile first!")
                return redirect(url_for("party"))

        elif request.method == "POST":
           
            partyDistrictProfile_exists = boundary.controller.DistrictExists(request.form, session["party"])
            if partyDistrictProfile_exists == False:
                error, result =  boundary.controller.createDistrictProfile(request.form, request.form.getlist, request.files.getlist)
                if result:
                    flash("Profile successfully created!")
                    contestingZones = boundary.controller.getContestingZones()
                    data = boundary.controller.getAll(session["party"])
                    return boundary.partyDistrictTemplateCreate(session["party"], data , contestingZones)

                else:
                    print(f"In main result : {error}")
                    flash(error)
                    contestingZones = boundary.controller.getContestingZones()
                    return boundary.partyDistrictTemplateCreate(session["party"],contestingZones)
            else:
                flash("Disctrict profile already exists, please select update to edit profile!")
                return redirect(url_for("party"))

           
                
    else:
        flash("login first!")
        return redirect(url_for("index")) """

#getDistrict
"""    
@app.route("/Party/getDistrict", methods=["GET", "POST"])
def getDistrict():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
            print("in get district")
            contestingZones = boundary.controller.getDistricts()
            return boundary.partyGetDistrict(contestingZones)
                

        elif request.method == "POST":
            if boundary.controller.DistrictExists(request.form, session["party"]):
                #print("in post")
            
                data = boundary.controller.getCandidatesByDistrict(request.form, session["party"])
                session["selectedDistrictCandidates"] = data
                #print(session["selectedDistrictCandidates"])
                return redirect(url_for("updateDistrictProfile"))

            else:
                flash("No record found, please create a profile for the district!")
                return redirect(url_for("party"))
    else:
        flash("login first!")
        return redirect(url_for("index"))

@app.route("/Party/getDistrict/UpdateProfile", methods=["GET", "POST"])
def updateDistrictProfile():
    boundary = PartyPage()
    
    if "username" in session:
        if request.method == "GET":
            #data = boundary.controller.getCandidatesByDistrict(request.form, session["party"])
            #session["selectedDistrictCandidates"] = data
            return boundary.partyDistrictTemplateUpdate(data =session["selectedDistrictCandidates"])
                

        elif request.method == "POST":
            images = request.files.get('img')
            print(f"here {images}")
            boundary.controller.updateDistrict(request.files.getlist, request.form.getlist)
            flash("District profile successfully updated!")
            return redirect(url_for("party"))
    else:
        flash("login first!")
        return redirect(url_for("index")) """

@app.route("/Party/viewDistrict", methods=["GET", "POST"])
def PartyViewDistrict():
    boundary = PartyPage()
    districts =  PartyPage().controller.getDistricts() #get only existing districts
    if request.method == "GET":
        return boundary.partyTemplateViewDistricts(districts, session["party"])
    
    elif request.method == "POST":
        session["show_candidates"], session["currentDistrict"] = PartyPage().controller.getCandidatesByDistrictToView(request.form)

        print(session["show_candidates"])
        return redirect(url_for("PartyViewCandidates"))

@app.route("/Party/viewDistrict/viewCandidates", methods=["GET", "POST"])
def PartyViewCandidates():
    boundary = PartyPage()
    districts =  PartyPage().controller.getDistricts()
    if request.method == "GET":
        return boundary.partyTemplateViewCandidates(districts, session["show_candidates"], session["currentDistrict"], session["party"] )
    
    elif request.method == "POST":
        session["show_candidates"], session["currentDistrict"] = PartyPage().controller.getCandidatesByDistrictToView(request.form)
        print(session["show_candidates"])
        return redirect(url_for("PartyViewCandidates"))

### VOTER PAGE ###
@app.route("/voter", methods=["GET", "POST"])
def voter():
    boundary = VoterPage()
    #name = VoterPage().controller.getName()
    if request.method == "GET":
        if "username" in session:
            details = VoterPage().controller.getDetails()
            return boundary.voterTemplate(session["username"], details)
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        print("12345")
        return boundary.buttonClicked(request.form)

### VOTER UPDATE ADDRESS PAGE ###
@app.route("/voter/updateAddress", methods=["GET", "POST"])
def voterUpdateAddress():
    boundary = VoterPage()
    if request.method == "GET":
        details = VoterPage().controller.getDetails()
        return boundary.voterTemplateUpdateAddress(session["username"], details)

    elif request.method == "POST":
        boundary.controller.setAddress(request.form)
        return redirect(url_for("voter"))

### VOTER UPDATE ADDRESS PAGE ###
@app.route("/voter/updatePhoneNumber", methods=["GET", "POST"])
def voterUpdatePhoneNumber():
    boundary = VoterPage()
    if request.method == "GET":
        details = VoterPage().controller.getDetails()
        return boundary.voterTemplateUpdatePhoneNumber(session["username"], details)

    elif request.method == "POST":
        boundary.controller.setPhoneNumber(request.form)
        return redirect(url_for("voter"))

@app.route("/voterViewParties", methods=["GET", "POST"])
def voterViewParties():
    boundary = VoterPage()
    parties = VoterPage().controller.getParties()
    if request.method == "GET":
        return boundary.voterTemplateViewParties(session["username"], parties, session['districtName'])
    
    elif request.method == "POST":
        session["candidates"] = VoterPage().controller.getCandidatesByDistrict(request.form)
        print(session["candidates"])
        return redirect(url_for("voterViewCandidates"))

@app.route("/voterViewCandidates", methods=["GET", "POST"])
def voterViewCandidates():
    boundary = VoterPage()
    parties = VoterPage().controller.getParties()
    chosen_party = VoterPage().controller.getSelectedParty()
    print(session["candidates"])
    if request.method == "GET":
        return boundary.voterTemplateViewCandidates(session["username"], parties, session['districtName'], session["candidates"], chosen_party=chosen_party)
    
    elif request.method == "POST":
        session["candidates"] = VoterPage().controller.getCandidatesByDistrict(request.form)
        return redirect(url_for("voterViewCandidates"))

@app.route("/voterVote", methods=["GET", "POST"])
def voterVote():
    boundary = VoterPage()
    parties = VoterPage().controller.getParties()
    constituency = VoterPage().controller.getConstituency()
    print(constituency)
    
    if request.method == "GET":
        return boundary.voterTemplateVoteParty(session["username"], parties,constituency)
    
    elif request.method == "POST":
        new_constituency = str(constituency)[2:-2]
        
        session["party"] = VoterPage().controller.voterVote(request.form.get("parties"),new_constituency,parties)
        print(constituency)
        print(request.form.get("parties"))
        flash("You have successfully voted")
        return redirect(url_for("voter"))

### VOTER PAGE ###
@app.route("/voterLiveVotes", methods=["GET", "POST"])
def voterLiveVotes():
    boundary = VoterPage()
    #name = VoterPage().controller.getName()
    if request.method == "GET":
        if "username" in session:
            details = VoterPage().controller.getDetails()
            constituency = VoterPage().controller.getDistrictName()
            liveResult = VoterPage().controller.getLiveResult(constituency)
            print("From main:\n")
            print(liveResult)
            return boundary.voterTemplateVoteLive(session["username"], details, constituency,liveResult)
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        print("12345")
        return boundary.buttonClicked(request.form)

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
