### IMPORTS ###
import time
#from fhe import *
import decimal
from re import sub
from decimal import Decimal
from inspect import _void
from random import vonmisesvariate
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import requests
import dropbox
import base64
import json
from PIL import Image
import numpy as np
import io
import os
import requests
import pyotp
import time 
from twilio.rest import Client 

app = Flask(__name__)
app.config['UPLOAD FOLDER'] = os.path.join(os.getcwd(), "static/photos")
### POSTGRESQL CONFIG ###
'''
db_host = 'db-postgresql-sgp1-68432-do-user-13104720-0.b.db.ondigitalocean.com'
db_name = 'defaultdb'
db_user = 'doadmin'
db_pw = 'AVNS_dzEhcpyafmLeNwHBmDN'
'''
###AWS POSTGRESQL CONFIG###
db_host = "fyp-22-s4-30.cuhxaq43l2oj.ap-southeast-1.rds.amazonaws.com"
db_name = 'postgres'
db_user = 'evotingsystem'
db_pw = 'EmXAdCIbKic5IL6TL9e3'

#key_pairs = fhe()
global otp_dic
otp_dic = {}

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


### Use Case 1 (LOGIN) ###
class LoginPage:
    def __init__(self) -> None:
        self.controller = LoginPageController()
        self.user_exist = False

    def loginTemplate(self):
        # get all profiles
        profiles = self.controller.getProfiles()
        parties = self.controller.getParties()
        return render_template("voter-login.html", profiles=profiles, parties=parties)

    def registerTemplate(self):
        return render_template("voter-register-form.html")

    def registerTemplateOTP(self):
        return render_template("voter-login-o-t-p.html")

    def redirectToProfilePage(self,account_type):
        default_profiles = ["party", "super_admin", "voter", 'admin']
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))

    def redirectToResetPasswordPage(self):
        return redirect(url_for("resetPassWord"))

    def redirectToRegisterPage(self):
        return redirect(url_for("register"))

class LoginPageController:
    def __init__(self) -> None:
        self.entity = UserAccount()

    def getCredentials(self, request_form) -> bool:
        
        self.entity.username = request_form["username"]
        self.entity.password = request_form["password"]
        self.entity.account_type = request_form["type"]

        if request_form["type"] == "party":
            #print("here " + request_form["party"])
            self.entity.party = request_form["party"]

        return self.entity.doesUserExist()

    def redirectPage(account_type):
        default_profiles = ["party", "admin", "voter", "super_admin"]
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))
    def getProfiles(self) -> list:
        return self.entity.getAllProfiles()

    def getParties(self):
        return self.entity.getAllParties()

    def sendOTPtouser(self, request_form):
        otp = self.entity.generateOTP()
        #self.entity.OTPPhoneNumber = '91251636'
        self.entity.OTPPhoneNumber = request_form["number"]
        account_sid = 'AC4fe73199e1fc12a01e04f1ddb53c18c3' 
        auth_token = '55efccda2ef34ba35881eb256df476ae' 
        client = Client(account_sid, auth_token) 
        
        message = client.messages.create(  
                                    messaging_service_sid='MGf788a76f1546ed9cbf819f1ab5ba9f44', 
                                    body=f'Your OTP IS {otp}',      
                                    to=f'+65{self.entity.OTPPhoneNumber}' 
                                ) 
        otp_dic[self.entity.OTPPhoneNumber] = otp
        print(message)

    def register(self,username,password,nric,name,postal_code,address,number):
        return self.entity.registerVoter(username,password,nric,name,postal_code,address,number)


class UserAccount():
    def getAllProfiles(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT profile_name FROM public."Profile"')
                profiles = cursor.fetchall()
        return profiles

    def doesUserExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                if self.account_type == "party":
                    #check if party's name is correct
                    print("party name:" + self.party)
                    cursor.execute(f'SELECT * FROM public."Login" WHERE username = %s AND password = %s AND name = %s AND profile = %s', (self.username, self.password, self.party, self.account_type))
                    result = cursor.fetchone()
                    db.commit()
                
                else:
                    cursor.execute(f'SELECT * FROM public."Login" WHERE username = %s AND password = %s AND profile = %s', (self.username, self.password, self.account_type))
                    result = cursor.fetchone()
                    db.commit()
                    print(result)
                    print(self.username)
                    print(self.password)
                    print(self.account_type)

                if result != None: return True
                else: return False

    def getAllParties(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Party_name" FROM public."Party"')
                parties = cursor.fetchall()
                print(parties)
        return parties

    def generateOTP(self):
        secret = pyotp.random_base32()
        #set code expiry to 60 secs
        totp = pyotp.TOTP(secret, interval=60)
        otp = totp.now() # => 6 digit number
        return otp

    
    def registerVoter(self,username,password,nric,name,postal_code,address,number):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('INSERT INTO public."Login" ("username", "password", "name", "profile") VALUES (%s, %s, %s, %s)', (username,password,name,"voter", ))
                cursor.execute('INSERT INTO public."Voter" ("nric", "name", "address", "postal_code","phone_number","voted") VALUES (%s, %s, %s, %s, %s, %s)', (nric,name,address,postal_code,number,"false", ))
                db.commit()

### party Use case ###
class PartyPage:
    def __init__(self) -> None:
        self.controller = PartyPageController()

    def partyTemplate(self, username, party, partyDetails):
        return render_template("partyHome.html", username=username, party=party, partyDetails= partyDetails)

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]
        #button_value = request_form["edit_remove"]

        if self.button_id=="b1":
            return redirect(url_for("CreatePartyProfile"))
        elif self.button_id == "b2":
            return redirect(url_for("UpdatePartyProfile"))
        elif self.button_id == "b3":
            return redirect(url_for("CreateDistrictProfile"))
        elif self.button_id == "b4":
            return redirect(url_for("getDistrict"))
        elif self.button_id == "b5":
            return redirect(url_for("PartyViewDistrict"))
        elif self.button_id == "b6":
            return redirect(url_for("Test")) # change fn name
        else:
            if self.button_id.split("_")[1] == "edit":
                session["districtName"] = self.button_id.split("_")[0]
                return redirect(url_for("Edit"))
            """ elif self.button_id.split("_")[1] == "remove":
                session["districtName"] = self.button_id.split("_")[0]
                return redirect(url_for("Remove")) """
       

   

    def partyTemplateProfileCreate(self, party):
        return render_template("partyProfileCreate.html", party=party)
    
    def updatePartyTemplate(self, party):
        return render_template("partyUpdateProfile.html", party=party)
    
    def partyDistrictTemplateCreate(self, party, data, zones):
        return render_template("partyDistrictCreate.html", party=party, data = data , zones = zones)

    def partyDistrictTemplateModal(self, party, data , zones):
        return render_template("addDistrictModal.html", party=party, data= data, zones = zones)

    def partyGetDistrict(self, zones):
        return render_template("partyGetDistrict.html", zones = zones)
    
    def getDistrictForm(self):
        return redirect(url_for("updateDistrictProfile"))
    
    def partyDistrictTemplateUpdate(self, data):
        return render_template("partyDistrictUpdate.html", data=data)
    
    def partyTemplateViewDistricts(self, districts, party):
        return render_template("partyViewDistricts.html", districts=districts, party=party)
    
    def partyTemplateViewCandidates(self, districts, candidates, currentDistrict, party):
        return render_template("partyViewCandidates.html", districts=districts, candidates=candidates, currentDistrict = currentDistrict, party = party)

    #def partyEditDistrictTemplateModal(self, data):
        #return render_template("updateDistrictModal.html", data=data)

# Party Controller    
class PartyPageController:
    def __init__(self) -> None:
        self.entity = PartyDetails()
    
    def getPartyDetails(self):
        return self.entity.partyDetailsAll()

    def getName(self):
        return self.entity.PartyName()

    def getDistricts(self):
        return self.entity.PartyDistricts()

    def ProfileExists(self, party) -> bool:
        self.entity.party = party
        return self.entity.CheckPartyExist()

    def DistrictExists(self, request, party) -> bool:
        self.entity.district = request["districtName"]
        self.entity.party = party
        return self.entity.CheckDistrictExist()

    def createPartyProfile(self,request, requestImg):

        self.entity.party = request["PartyName"]
        self.entity.manifesto = request["PartyManifesto"]
        self.entity.logo = requestImg["logo"]

        return self.entity.createNewPartyProfile()

    def updatePartyProfile(self, request, requestImg ,party):
        self.entity.manifesto = request["PartyManifesto"]
        self.entity.logo = requestImg["logo"]
        self.entity.party = party

        return self.entity.updateProfileParty()
    
    def createDistrictProfile(self, request, request_list, requestImg) -> list:
        
        self.entity.nric=request_list("NRIC[]")
        self.entity.name=request_list("Name[]")
        #self.entity.image=request_list("img[]")
        self.entity.image = requestImg("img[]")

        self.entity.partyName = request["PartyName"]
        self.entity.districtName = request["districtName"]
        return self.entity.createNewDistrictProfile()
    

    def getCandidatesByDistrict(self, party):
        self.entity.districtName = session["districtName"]
        self.entity.party = party
        #session["districtName"] = self.entity.districtName
        session["party"] = self.entity.party
        return self.entity.getCandidates()

    def getCandidatesByDistrictToView(self, request):
        self.entity.districtToView = request["districtName"]
        return self.entity.getCandidatesToView()

    def updateDistrict(self, request, request_list):
        self.entity.Oldnric=request_list("oldNRIC[]")
        self.entity.Oldname=request_list("oldName[]")

        self.entity.nric=request_list("newNRIC[]")
        self.entity.name=request_list("newName[]")
    
        self.entity.image = request("img[]")
        self.entity.party = session["party"]
        self.entity.districtName = session["districtName"]
        return self.entity.updateNewDistrictProfile()

    def getContestingZones(self):
        return self.entity.getDbDistrictName()

    def getImages(self, filepath,):
        return self.entity.load_image(filepath)

    def getAll(self, party):
        self.entity.party = party
        return self.entity.getAllDistrictData()
        
    def delete(self, party, district):
        self.entity.party = party
        self.entity.district = district
        return self.entity.deleteData()


#Party Entity
class PartyDetails:
    def deleteData(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('DELETE FROM public."PartyElectionArea" WHERE "election_area" = %s and "party" = %s',(self.district, self.party, ))
                cursor.execute('DELETE FROM public."Candidate" WHERE "DistrictName" = %s and "Party_name" = %s',(self.district, self.party, ))
                db.commit()


    #get Candidate's data from specific district 
    def getAllDistrictData(self):
        result = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                districts = self.PartyDistricts()
                for district in districts:
                    cursor.execute('SELECT * FROM public."Candidate" WHERE "Party_name" = %s and "DistrictName" = %s ' ,(self.party,district, ))
                    temp = cursor.fetchall()
                    result.append(temp)
        return result

    #get party's data
    def partyDetailsAll(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."Party" WHERE "Party_name" = %s',(session["party"],))
                result = cursor.fetchone()
                print(result)
                return result

    #get already contested district 
    def PartyDistricts(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT DISTINCT "DistrictName" FROM public."Candidate" WHERE "Party_name" = %s',(session["party"],))
                result = cursor.fetchall()
                if result == [[]]:
                    return None
                else:
                    result = list(map(lambda x: x[0], result))
                    return result

    def uploadImagePartyLogo(self):

        img1 = Image.open(self.logo)
        img1 = img1.resize((512, 512))
        
        filename = secure_filename(self.party + ".png")
        
        img1.save(os.path.join(app.config['UPLOAD FOLDER'], self.party + ".png"))

    def uploadImageCandidate(self):
        for i in range(len(self.image)):
            img1 = Image.open(self.image[i])
            img1 = img1.resize((512, 512))
            img1.save(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.nric[i] + ".png")))
        
    def getCandidatesToView(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT "Name", "Image" FROM public."Candidate" WHERE "DistrictName" = %s AND "Party_name" = %s;', (self.districtToView, session["party"]))
                result = cursor.fetchall()
                return result, self.districtToView

    def getDbDistrictName(self):
        result = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                existing = self.PartyDistricts() # get already contested district

                cursor.execute('SELECT * FROM public."ContestingZone" ORDER BY "DistrictName" ASC')
                districts = cursor.fetchall()

                for district in districts:
                    if district[0] not in existing:
                        result.append(district[0])
        return result 

    
    def PartyName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name FROM public."Login" WHERE profile = "Party"; ')
                result = cursor.fetchall()
                db.commit()
               
                return result

    def CheckPartyExist(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."Party" WHERE "Party_name" = %s ;', (self.party,))
                result = cursor.fetchone()
                print(result)
                db.commit()

                if result != None: 
                    return True #there is a result, hence party already exists
                else: 
                    return False

    def CheckDistrictExist(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT COUNT("DistrictName") FROM public."Candidate" WHERE "DistrictName" = %s AND "Party_name" = %s group by "Party_name";', (self.district, self.party,))
                result = cursor.fetchone()
                print(result)
                db.commit()

                #print(len(result))
                if result != None: 
                    return True #there is a result, hence party already exists
                else: 
                    return False

    def createNewPartyProfile(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('INSERT INTO public."Party" ("Party_name", "Manifesto", "Logo") VALUES (%s, %s, %s)', (self.party, self.manifesto, self.party + ".png", ))
                db.commit()
                self.uploadImagePartyLogo()
        

    def updateProfileParty(self):
        print(self.manifesto)
        print((self.logo))
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:     
                if self.manifesto and self.logo.filename != "":
                    cursor.execute('UPDATE public."Party" set "Logo" = %s , "Manifesto" = %s WHERE "Party_name" = %s', (self.party + ".png", self.manifesto, self.party, ))
                    db.commit()
                    self.uploadImagePartyLogo()
                elif self.manifesto == "" and self.logo.filename != "": 
                    cursor.execute('UPDATE public."Party" set "Logo" = %s WHERE "Party_name" = %s', (self.party + ".png", self.party, ))
                    db.commit()
                    self.uploadImagePartyLogo()
                elif self.logo.filename == "" and self.manifesto !="": 
                    cursor.execute('UPDATE public."Party" set "Manifesto" = %s WHERE "Party_name" = %s', (self.manifesto, self.party, ))
                    db.commit()
                else:
                    return
     

    def createNewDistrictProfile(self):
        #print("here")
        print(self.nric)
        print(self.name)
        print(self.image)

        existing_candidate = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                #check if candidate is already registered
                for i in range(len(self.nric)):
                    nric = self.nric[i]
                    cursor.execute('SELECT * FROM public."Candidate" WHERE "NRIC" = %s ;',(nric,))
                    candidate = cursor.fetchone()

                    if candidate == None:
                        continue
                
                    else:
                        existing_candidate.append(candidate)

        #insert candidates to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                if len(existing_candidate) == 0:
                    for i in range(len(self.nric)):
                        nric = self.nric[i]
                        name = self.name[i]
                        image = self.nric[i] + ".png"
                        cursor.execute('INSERT INTO public."Candidate" ("NRIC", "Name", "Image", "Party_name", "DistrictName") VALUES (%s, %s, %s, %s, %s)', (nric, name, image, self.partyName, self.districtName, ))
                        db.commit()
                        self.uploadImageCandidate()

                else:
                    return existing_candidate, False
            
        return existing_candidate, True


    def getCandidates(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."Candidate" WHERE "Party_name" = %s AND "DistrictName" = %s ', (self.party, self.districtName, ))
                result = cursor.fetchall()
                #print(result)
        return result

    def updateNewDistrictProfile(self):
        print(self.Oldnric)
        print(self.Oldname)

        print(self.nric)
        print(self.name)
        print(self.image)


        #run a validation check on existing nric with the new updated nric
        existing_candidate = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                #check if candidate is already registered
                for i in range(len(self.nric)):
                    nric = self.nric[i]
                    cursor.execute('SELECT * FROM public."Candidate" WHERE "NRIC" = %s ;',(nric,))
                    candidate = cursor.fetchone()

                    if candidate == None:
                        continue
                
                    else:
                        existing_candidate.append(candidate)
                
        if len(existing_candidate) == 0:
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    for i in range(len(self.Oldnric)):
                        #new nric field is not blank and image is blank
                        if self.nric[i] != "" and self.image[i].filename == "":
                            #Open image of old file using old nric
                            img1 = Image.open(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))

                            #Update candidate old nric column with new nric 
                            cursor.execute('UPDATE public."Candidate" SET "NRIC" = %s WHERE "NRIC" = %s',(self.nric[i], self.Oldnric[i],))

                            #Update candidate old image path with new iamge path
                            cursor.execute('UPDATE public."Candidate" SET "Image" = %s WHERE "NRIC" = %s',(self.nric[i] + ".png", self.nric[i],))

                            #save iamge as new image file name
                            img1.save(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.nric[i] + ".png")))

                            #delete old image
                            os.remove(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))

                        #new nric field is blank and image is not blank
                        if self.nric[i] == "" and self.image[i].filename != "":
                            #Open image of old file using old nric
                            img1 = Image.open(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))
                            
                            #Update candidate old image path with new iamge path **technically file name remains the same
                            cursor.execute('UPDATE public."Candidate" SET "Image" = %s WHERE "NRIC" = %s',(self.Oldnric[i] + ".png", self.Oldnric[i],))

                            img1 = Image.open(self.image[i])
                            img1 = img1.resize((512, 512))

                            #save img as new image file name **replace the files too since using same object instance
                            img1.save(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))

                        #new nric field is not blank and image field is not blank
                        if self.nric[i] != "" and self.image[i].filename != "":
                            #self.updateCandidateImage(i)
                            #Update image old image path, old nric, old name
                            img1 = Image.open(self.image[i])
                            img1 = img1.resize((512, 512))
                            #cursor.execute('UPDATE public."Candidate" SET "Image" = %s WHERE "NRIC" = %s AND "Name" = %s',(self.Oldnric[i] + ".png", self.Oldnric[i], self.Oldname[i],))
                            cursor.execute('UPDATE public."Candidate" SET "Image" = %s WHERE "NRIC" = %s',(self.nric[i] + ".png", self.Oldnric[i],))
                        #
                            #Update candidate old nric column with new nric 
                            cursor.execute('UPDATE public."Candidate" SET "NRIC" = %s WHERE "NRIC" = %s',(self.nric[i], self.Oldnric[i],))

                            img1.save(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.nric[i] + ".png")))
                            os.remove(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))
                            
                            #else:
                            #   img1.save(os.path.join(app.config['UPLOAD FOLDER'], secure_filename(self.Oldnric[i] + ".png")))


                        #set name column to new name in db
                        if self.name[i] != "":
                            cursor.execute('UPDATE public."Candidate" SET "Name" = %s WHERE "Name" = %s AND "NRIC" = %s',(self.name[i], self.Oldname[i], self.Oldnric[i],))

                        
                    db.commit() 
                    return existing_candidate, True

        else:
            return existing_candidate, False
            


    

### voter Use case ###
class VoterPage:
    def __init__(self) -> None:
        self.controller = VoterPageController()
        
    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]
        if self.button_id == "b1":
            return redirect(url_for("voterUpdateAddress"))
        if self.button_id == "b2":
            return redirect(url_for("voterUpdatePhoneNumber"))
        if self.button_id == "b3":
            return redirect(url_for("voterViewParties"))
        if self.button_id == "b4":
            print("In after click button")
            print(self.controller.hasVoterVoted()[0])
            if(self.controller.hasVoterVoted()[0]==True):
                print("Voter voted")
                flash("You have already voted")
                return redirect(url_for("voter"))
            else:
                print("Hevent vote")
                return redirect(url_for("voterVote"))
        elif self.button_id =='return':
            return redirect(url_for("index"))
        
        
        elif self.button_id =='return':
            return redirect(url_for("index"))


    def voterTemplate(self, username, details):
        #return render_template("voterHome.html", username=username, details=details, constituency=constituency)
        return render_template("web-voter-homepage.html", username=username, details=details)

    def voterTemplateUpdateAddress(self, username, details):
        return render_template("voterUpdateAddress.html", username=username,details=details)

    def voterTemplateUpdatePhoneNumber(self, username, details):
        return render_template("voterUpdatePhoneNumber.html", username=username, details=details)

    def voterTemplateViewParties(self, username, parties, district):
        #return render_template("voterViewParties.html", username=username, parties=parties)
        return render_template("view-party-info.html", username=username, parties=parties, district=district)
    
    def voterTemplateViewCandidates(self, username, parties, district, candidates, chosen_party):
        #return render_template("voterViewCandidates.html", username=username, parties=parties, candidates=candidates, chosen_party=chosen_party)
        return render_template("view-candidate-info.html", username=username, parties=parties, district=district,  candidates=candidates, chosen_party=chosen_party)
    
    def voterTemplateVoteParty(self,username,parties,constituency):
        return render_template("voterVote.html",username=username,parties=parties,constituency=constituency)
    
    def voterTemplateVoteLive(self, username, details, constituency, liveResult):
        return render_template("voterLiveVotes.html", username=username, details=details, constituency=constituency, liveResult=liveResult)

    
class VoterPageController:
    def __init__(self) -> None:
        self.entity = VoterDetails()

    def getDetails(self):
        return self.entity.voterDetails()

    def setAddress(self, request):
        streetName = str(request["streetName"]).split(" ")
        postal_code = streetName[-1]
        streetName = streetName[:-2]
        print(streetName)
        self.entity.address = " ".join(streetName) + " " + str(request["unitNumber"])
        self.entity.postal_code = postal_code
        return self.entity.voterNewAddress()

    def setPhoneNumber(self, request):
        self.entity.phone_number = request["phone_number"]
        return self.entity.voterNewPhoneNumber()

    def getDistrictName(self):
        return self.entity.voterDistrictName()

    def getCandidatesByDistrict(self, request):
        self.entity.districtName = self.getDistrictName()
        self.entity.chosen_party = request["parties"]
        session["chosen_party"] = self.entity.chosen_party
        return self.entity.voterGetCandidatesByDistrict()

    def getParties(self):
        return self.entity.voterGetParties()

    def getSelectedParty(self):
        return self.entity.voterGetSelectedParty()

    def getConstituency(self):
        return self.entity.voterGetConstituency()

    def voterVote(self,request,constituency,parties):
        #self.entity.chosen_party = request.form.get("parties")
        #session["chosen_party"] = self.entity.chosen_party
        self.entity.addedToBallot(request,parties,constituency)
        return self.entity.voterVote(request,constituency)

    def hasVoterVoted(self):
        return self.entity.hasVote()

    def getLiveResult(self,constituency):
        return self.entity.liveResult(constituency)

vote_count = 0
class VoterDetails:
    def voterDetails(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name, address, postal_code, phone_number, "contestingZone", "voted" FROM public."Voter" WHERE nric = %s; ', (session["username"],))
                result = cursor.fetchone()
                db.commit()
                session['districtName'] = result[4]
                return result

    def voterNewAddress(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                print("testing")
                url = f"https://www.parliament.gov.sg/mps/find-mps-in-my-constituency?SearchKeyword={self.postal_code}"
                fp = requests.get(url).text
                soup = BeautifulSoup(fp, 'html.parser')
                contestingZone = soup.find("div" , {"class" : "row result-grc result-pd"}).find("h4").find("a").text
                cursor.execute(f'UPDATE public."Voter" SET address = %s , postal_code = %s, "contestingZone" = %s WHERE nric = %s; ', (self.address, self.postal_code, contestingZone , session["username"],))
                db.commit()
    
    def voterNewPhoneNumber(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'UPDATE public."Voter" SET phone_number = %s WHERE nric = %s; ', (self.phone_number, session["username"],))
                db.commit()
                print("testing")

    def voterDistrictName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "contestingZone" FROM public."Voter" WHERE nric = %s;', (session["username"],))
                result = cursor.fetchone()
                return result[0]

    def voterGetCandidatesByDistrict(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Name", "Party_name", "Image", "DistrictName" FROM public."Candidate" WHERE "DistrictName" = %s AND "Party_name" = %s;', (self.districtName,self.chosen_party))
                result = cursor.fetchall()
                #print(type(result[0][1]))
                
                return result

    def voterGetParties(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                session['districtName'] =  self.voterDistrictName()
                cursor.execute(f'SELECT "party" FROM public."PartyElectionArea" WHERE "election_area" = %s;', (session['districtName'],))
                
                result = cursor.fetchall()
                return result

    def voterGetSelectedParty(self):
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Party_name", "Manifesto", "Logo" FROM public."Party" WHERE "Party_name" = %s;', (session["chosen_party"],))
                result = cursor.fetchone()
                
                return result
    
    def voterVote(self,selected_party,constituency):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                toVoteArr=[]
                
                cursor.execute(f'UPDATE public."Voter" SET voted=true')
                db.commit()
                
                
                print("To insert... : " + str(selected_party) + " constituency: " + str(constituency))
                toVoteArr.append(selected_party)
                toVoteArr.append(constituency)
                print(toVoteArr)

                cursor.execute(f'SELECT "voted_party", "contestingZone" FROM public."Votes" ')
                result = cursor.fetchall()
                print("printing select")
                print(result)
                
                print("End of printing select")
                db.commit()

                if(toVoteArr in result):
                    print("Consituency and Party exist")
                    cursor.execute(f'SELECT vote_count FROM public."Votes" WHERE voted_party = %s AND "contestingZone"=%s;',(selected_party,constituency,))
                    vote_count_from_db = cursor.fetchone()
                    print(vote_count_from_db[0])
                    vote_from_db = int(vote_count_from_db[0])
                    vote_count_to_insert = vote_from_db+1
                    cursor.execute(f'UPDATE public."Votes" SET vote_count=%s WHERE voted_party = %s AND "contestingZone" = %s;',(vote_count_to_insert,selected_party,constituency,))
                    db.commit()
                else:
                    print("Consituency and Party DOES NOT exist")
                    voter_count = vote_count + 1
                    cursor.execute(f'INSERT INTO public."Votes"(voted_party, "contestingZone", vote_count)VALUES (%s, %s, %s);',(selected_party,constituency,voter_count,))
                    print("Voter voted!")
                    db.commit()
    def hasVote(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "voted" FROM public."Voter"')
                result = cursor.fetchone()
                
                db.commit()
                print("Voter voted!")
                return result
                
    def voterGetConstituency(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "contestingZone" FROM public."Voter"')
                result = cursor.fetchone()
                
                db.commit()
                return result

    def addedToBallot(self, election_party_title, parties, constituency):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                for i in parties:
                    
                    if i[0] == election_party_title:
                        x = 1
                    else:
                        x = 0
                    ciph = key_pairs.fhe_encrypt([x,x,x,x], constituency, i[0], "election1")
                    cursor.execute(f'INSERT INTO public."Ballot"(election_area_title, election_party_title, election_title, encrypted_value_c0, encrypted_value_c1, "time_stamp") VALUES (%s, %s, %s, %s, %s, %s);', (constituency, i[0], "election1", f"{constituency}_{i[0]}_election1_c0.txt", f"{constituency}_{i[0]}_election1_c1.txt",datetime.datetime.now(),))

    def liveResult(self,constituency):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT voted_party,vote_count FROM public."Votes" WHERE "contestingZone"=%s',(constituency,))
                result = cursor.fetchall()
                db.commit()
                print(result)
                arrFinal=[]
                final_str = ""
                for i in result:
                    print(i)
                    final_result = str(i)[1:-1]
                    final_final = final_result.replace("'","")
                    final_final_result = final_final.replace(",","")
                    print(final_final_result)
                    print(type(final_final_result))
                    final_str += final_final_result + "\n" 
                print("Printing final str")
                print(final_str)
                return final_str
                
                #return result


### superadmin Use case ###
class superadminPage:
    def __init__(self) -> None:
        self.controller = superadminControllerPage()

    def superadminTemplate(self, data):
        return render_template("superadminHome.html", data=data)

    
class superadminControllerPage:
    def __init__(self) -> None:
        self.entity = superadminDetails()

    #def getName(self):
    #    return self.entity.candidateName()
    def createAdmin(self,admin_username,admin_password,admin_name):
        return self.entity.createAdmin(admin_username,admin_password,admin_name)

    def get_admin(self)->list:
        return self.entity.retrieveAdmin()

    def delete_admin(self,username)->list:
        return self.entity.deleteAdmin(username)


class superadminDetails:

    def retrieveAdmin(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                result = cursor.fetchall()
                db.commit()
                return result

    def deleteAdmin(self,username):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'DELETE from public."Login" where profile = %s AND username = %s;',('admin',username,))
                db.commit()
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                
                db.commit()
                result = cursor.fetchall()
                return result

    def createAdmin(self,admin_username,admin_password,admin_name):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host, port=5432) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'INSERT INTO public."Login"(username,password,name,profile) VALUES(%s,%s,%s,%s);',(admin_username,admin_password,admin_name,'admin',))
                db.commit()
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                db.commit()
                result = cursor.fetchall()
                return result
