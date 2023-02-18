### MODULE IMPORTS ###

from tkinter import Menu
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from werkzeug.utils import secure_filename
from classes import * # import all classes from classes.py
from app import app
from app import db
from admin.blueprint import admin
#import views
global OTPPhoneNumber
global otp
global totp
OTPPhoneNumber = ""
otp = ""
totp = ""



app.register_blueprint(admin, url_prefix='/admin')
'''
### POSTGRESQL CONFIG ###
db_host = 'satao.db.elephantsql.com'
db_name = 'jwwfjrox'
db_user = 'jwwfjrox'
db_pw = 'jQiFAyGF07Tghwk44c4GButvW2uKzsLi'

### POSTGRESQL CONFIG ###
db_host = 'ec2-34-234-240-121.compute-1.amazonaws.com'
db_name = 'dcgsvhb0enfgfd'
db_user = 'ampoosmqdvdzte'
db_pw = '1494a152d2acffe248186b855286562322f43ab69a4ae0cd1b061bef24f36bf3'
'''
###AWS POSTGRESQL CONFIG###
db_host = "fyp-22-s4-30.cuhxaq43l2oj.ap-southeast-1.rds.amazonaws.com"
db_name = 'postgres'
db_user = 'evotingsystem'
db_pw = 'EmXAdCIbKic5IL6TL9e3'

### SESSION CONFIG (password & period) ###

app.permanent_session_lifetime = timedelta(minutes=60)
#Logout
@app.route("/logOut")
def logOut():
    boundary = Logout(session)
    session.clear()
    print(session)
    return boundary.logUserOut() 


##admin page##
@app.route("/admin", methods=["GET", "POST"])
def admin():
    return render_template('index.html')

### LOGIN PAGE ###
@app.route("/", methods=["GET", "POST"])
def index():
    boundary = LoginPage()
    if request.method == "GET":
        print("In get")
        return boundary.loginTemplate() # A-B

    elif request.method == "POST":
        print("inside POST of login")
        if request.form["submit"] == "login":
            if boundary.controller.getCredentials(request.form): # B-C, C-E  
                print("inside inside POST of login")
                # login success - add username & account_type in session
                session["username"] = request.form["username"]
                session["account_type"] = request.form["type"]
                
                if request.form["type"] == "party":
                    session["party"] = request.form["party"]

                # redirect page to candidate, admin, voter
                return boundary.redirectToProfilePage(session["account_type"]) # C-B

            else:
                flash(request.form["username"] + " login failed!")
                return boundary.loginTemplate() # redirect to login page
        elif request.form["submit"] == "resetpw":
            return boundary.redirectToRegisterPage()
        elif request.form["submit"] == "register":
            return boundary.redirectToRegisterPage()
        elif request.form["submit"] == 'yes':
            return redirect(url_for("resultsViewDistrict"))
        elif request.form["submit"] == 'no':
            return redirect(url_for("index"))
        
        
        


@app.route("/loginOTP", methods=["GET", "POST"])
def loginOTP():
    boundary = LoginPage()
    if request.method == "GET":
        secret = pyotp.random_base32()
        #set code expiry to 60 secs
        totp = pyotp.TOTP(secret, interval=60)
        otp = totp.now() # => 6 digit number
        OTPPhoneNumber = boundary.controller.getUserPhone()
        account_sid = 'AC4fe73199e1fc12a01e04f1ddb53c18c3' 
        auth_token = '55efccda2ef34ba35881eb256df476ae' 
        client = Client(account_sid, auth_token) 
        print("Phone Number: ")
        print(OTPPhoneNumber)
        message = client.messages.create(messaging_service_sid='MGf788a76f1546ed9cbf819f1ab5ba9f44', body=f'Your OTP IS {otp}', to=f'+65{OTPPhoneNumber}')
        print(OTPPhoneNumber)
        print(otp)
        otp_arr = []
        for i in otp:
            otp_arr.append(f.encrypt(str(i).encode()))
        
        session["otp"] = otp_arr
        
        boundary.controller.setOTP(otp)
        return boundary.registerTemplateOTP()
    
    elif request.method =="POST":
        OTPkeyed = boundary.controller.getOTPInput(request.form)
        verify_otp = ""
        for i in session["otp"]:
            verify_otp += str(int(f.decrypt(i)))
        print(str(OTPkeyed))
        print(verify_otp)
        if (str(OTPkeyed) == verify_otp):
            print("ttue")
            return redirect(url_for('voter'))
        else:
            return redirect(url_for('loginOTP'))
            print("Wrong password")
            flash("Wrong password")

@app.route("/resetPassWord", methods=["GET", "POST"])
def resetPassWord():
    boundary = LoginPage()
    if request.method == "GET":
        print("In get")
        return boundary.loginTemplate() # A-B

@app.route("/register", methods=["GET", "POST"])
def register():
    boundary = LoginPage()
    if request.method == "GET":
        print("In get")
        return boundary.registerTemplate() # A-B

    if request.method =="POST":
        print(request.form)
        print("In post")
        session["userParticulars"] = boundary.controller.getRegisterationFormDetails(request.form)
        #boundary.controller.sendOTPtouser(request.form)
        return redirect(url_for("registerOTP"))
        #return boundary.registerTemplateOTP(request.form)

@app.route("/registerOTP", methods=["GET", "POST"])
def registerOTP():
    
    boundary = LoginPage()
    if request.method == "GET":
        #username = request.args.get("username")
        #print(username)
        #boundary.controller.sendOTPtouser(request.form)
        
        secret = pyotp.random_base32()
        #set code expiry to 60 secs
        totp = pyotp.TOTP(secret, interval=60)
        otp = totp.now() # => 6 digit number
        OTPPhoneNumber = session["userParticulars"][6]
        account_sid = 'AC4fe73199e1fc12a01e04f1ddb53c18c3' 
        auth_token = '55efccda2ef34ba35881eb256df476ae' 
        client = Client(account_sid, auth_token) 
        
        message = client.messages.create(messaging_service_sid='MGf788a76f1546ed9cbf819f1ab5ba9f44', body=f'Your OTP IS {otp}', to=f'+65{OTPPhoneNumber}')
        #print(session["OTPPhoneNumber"])
        print(otp)
        otp_arr = []
        for i in otp:
            otp_arr.append(f.encrypt(str(i).encode()))
        
        session["otp"] = otp_arr
        boundary.controller.setOTP(otp)
        #boundary.controller.setPhoneNumber(request.form)
        return boundary.registerTemplateOTP()

    elif request.method == "POST":
        OTPkeyed = boundary.controller.getOTPInput(request.form)
        verify_otp = ""
        for i in session["otp"]:
            verify_otp += str(int(f.decrypt(i)))
        print(str(OTPkeyed))
        print(verify_otp)
        if (str(OTPkeyed) == verify_otp):
            boundary.controller.getRegisterationFormDetailsFromGet()
            return redirect(url_for("index"))

        else:
            flash("Wrong Otp!")
            return redirect(url_for("registerOTP"))
        

        

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
                contestingZones = boundary.controller.getContestingZones(session["party"])
                print(f"contesting zones: {contestingZones}")
                data = boundary.controller.getAll(session["party"])
                print(f"contesting zones: {data}")
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
           
            contestingZones = boundary.controller.getContestingZones(session["party"])
            data = boundary.controller.getAll(session["party"])
            print("hereeeeee")
            print(f'zones : {contestingZones}')
    
            return boundary.partyDistrictTemplateModal(session["party"], data, contestingZones)
            

        elif request.method == "POST":
           
            #partyDistrictProfile_exists = boundary.controller.DistrictExists(request.form, session["party"])

            
            error, result =  boundary.controller.createDistrictProfile(request.form, request.form.getlist, request.files.getlist)
            if result:
                flash("Profile successfully created!")
                contestingZones = boundary.controller.getContestingZones(session["party"])
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
        session["OTPPhoneNumber"] = request.form["phone_number"]
        print(session["OTPPhoneNumber"])
        return redirect(url_for("OtpValidation"))
        

@app.route("/voter/OtpValidation", methods=["GET", "POST"])
def OtpValidation():
    boundary = VoterPage()
    if request.method == "GET":
        secret = pyotp.random_base32()
        #set code expiry to 60 secs
        totp = pyotp.TOTP(secret, interval=60)
        otp = totp.now() # => 6 digit number
        
        account_sid = 'AC4fe73199e1fc12a01e04f1ddb53c18c3' 
        auth_token = '55efccda2ef34ba35881eb256df476ae' 
        client = Client(account_sid, auth_token) 
        
        message = client.messages.create(messaging_service_sid='MGf788a76f1546ed9cbf819f1ab5ba9f44', body=f'Your OTP IS {otp}', to=f'+65{session["OTPPhoneNumber"]}')
        print(session["OTPPhoneNumber"])
        print(otp)
        otp_arr = []
        for i in otp:
            otp_arr.append(f.encrypt(str(i).encode()))
        
        session["otp"] = otp_arr
        boundary.controller.setOTP(otp)
        #boundary.controller.setPhoneNumber(request.form)
        return boundary.registerTemplateOTP()

    elif request.method == "POST":
        OTPkeyed = boundary.controller.getOTPInput(request.form)
        verify_otp = ""
        for i in session["otp"]:
            verify_otp += str(int(f.decrypt(i)))
        print(str(OTPkeyed))
        print(verify_otp)
        if (str(OTPkeyed) == verify_otp):
            boundary.controller.setPhoneNumber(session["OTPPhoneNumber"])
            return redirect(url_for("voter"))

        else:
            flash("Wrong Otp!")
            return redirect(url_for("OtpValidation"))
    

       

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

@app.route("/adminDecrypt", methods=["GET", "POST"])
def adminDecrypt():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminUploadSecretKeyTemplate()
    elif request.method == "POST":
        if boundary.controller.getFHESecretKey(request.files):
            fhe_fernet_key = open("./keys/fhe_fernet.key", "rb").read()
            f = Fernet(fhe_fernet_key)
            s3 = open('./keys/fernet_fhe.txt', 'r')
            contents = s3.read().splitlines()
            #print(contents)
            s3.close()
            write_decrypted_sk = open('./keys/s1.txt','w+')
            for i in contents:
                write_decrypted_sk.write(str(int(f.decrypt(i))) +'\n')
            write_decrypted_sk.close()
            key_pairs.uploadSecretKey()
            print("pass")
            boundary.controller.decryptVotesByDistrict(key_pairs)
            return redirect(url_for("resultsViewDistrict"))
        else:
            print("Wrong SK")

@app.route("/resultsViewDistrict", methods=["GET","POST"])
def resultsViewDistrict():
    boundary = ResultsPage()
    if request.method == "GET":
        districts = boundary.controller.getDistrict()
        return boundary.getResultsTemplate(districts=districts)
    
    if request.method == "POST":
        session["district_clicked"] = request.form["districts"]
        return redirect(url_for('resultsViewVote'))
        
@app.route("/resultsViewVote", methods=["GET","POST"])
def resultsViewVote():
    boundary = ResultsPage()
    if request.method == "GET":
        vote = boundary.controller.getAllResults()
        return boundary.getResultsViewVoteTemplate(vote=vote)
    
    
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
