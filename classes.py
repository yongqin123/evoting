### IMPORTS ###
import decimal
from re import sub
from decimal import Decimal
from inspect import _void
from random import vonmisesvariate
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
import requests
import dropbox
import base64
import json
from PIL import Image
import numpy as np
import io

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
        return render_template("login.html", profiles=profiles, parties=parties)

    def redirectPage(account_type):
        default_profiles = ["party", "super_admin", "voter"]
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))


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
        default_profiles = ["party", "admin", "voter"]
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))
    def getProfiles(self) -> list:
        return self.entity.getAllProfiles()

    def getParties(self):
        return self.entity.getAllParties()

class UserAccount():
    def getAllProfiles(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT profile_name FROM public."Profile"')
                profiles = cursor.fetchall()
        return profiles

    def doesUserExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
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
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Party_name" FROM public."Party"')
                parties = cursor.fetchall()
                print(parties)
        return parties

### party Use case ###
class PartyPage:
    def __init__(self) -> None:
        self.controller = PartyPageController()

    def partyTemplate(self, username, party):
        return render_template("partyHome.html", username=username, party=party)

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]

        if self.button_id=="b1":
            return redirect(url_for("CreatePartyProfile"))
        elif self.button_id == "b2":
            return redirect(url_for("UpdatePartyProfile"))
        elif self.button_id == "b3":
            return redirect(url_for("CreateDistrictProfile"))
        elif self.button_id == "b4":
            return redirect(url_for("getDistrict"))

    def partyTemplateProfileCreate(self, party):
        return render_template("partyProfileCreate.html", party=party)
    
    def updatePartyTemplate(self, party):
        return render_template("partyUpdateProfile.html", party=party)
    
    def partyDistrictTemplateCreate(self, party, zones):
        return render_template("partyDistrictCreate.html", party=party, zones = zones)

    def partyGetDistrict(self, zones):
        return render_template("partyGetDistrict.html", zones = zones)
    
    def getDistrictForm(self):
        return redirect(url_for("updateDistrictProfile"))
    
    def partyDistrictTemplateUpdate(self, data):
        return render_template("partyDistrictUpdate.html", data=data)
    
    

# Party Controller    
class PartyPageController:
    def __init__(self) -> None:
        self.entity = PartyDetails()
        

    def getName(self):
        return self.entity.PartyName()

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
        return self.entity.creatNewDistrictProfile()
    

    def getCandidatesByDistrict(self, request, party):
        self.entity.districtName = request["districtName"]
        self.entity.party = party
        return self.entity.getCandidates()

    def updateDistrict(self, request, request_list):
        self.entity.Oldnric=request_list("oldNRIC[]")
        self.entity.Oldname=request_list("oldName[]")

        self.entity.nric=request_list("newNRIC[]")
        self.entity.name=request_list("newName[]")
    
        self.entity.image = request("img[]")

        return self.entity.updateNewDistrictProfile()

    def getContestingZones(self):
        return self.entity.getDbDistrictName()

    def getImages(self, filepath,):
        return self.entity.load_image(filepath)

    


#Party Entity
class PartyDetails:
    def uploadImagePartyLogo(self):
        APP_KEY = 'v0bf0ml5z14xin8'
        APP_SECRET = 'hhmq6gksrwpxyfg'
        REFRESH_TOKEN = "vX79bzPwE64AAAAAAAAAAdaNN6MshBEAdGEJke6CfVizskRxQUi-nAyXKnmw8sVo"

        dbx = dropbox.Dropbox(
                    app_key = APP_KEY,
                    app_secret = APP_SECRET,
                    oauth2_refresh_token = REFRESH_TOKEN
                )
        print(dbx.users_get_current_account())


        files = dbx.files_list_folder("/Party Logo").entries
        files_list = []
        for file in files:
            if isinstance(file, dropbox.files.FileMetadata):
                metadata = {
                    'name': file.name,
                    'path_display': file.path_display,
                    'client_modified': file.client_modified,
                    'server_modified': file.server_modified
                }
                files_list.append(metadata)

        #print(files_list)
        img1 = Image.open(self.logo)
        img1 = img1.resize((512, 512))
        img1.save(self.party + ".png")
        image = self.load_image(self.logo)
        
        dbx.files_upload(image, f"/Party Logo/{self.party + '.png'}", mode=dropbox.files.WriteMode("overwrite") )

    def getDbDistrictName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."ContestingZone" ORDER BY "DistrictName" ASC')
                result = cursor.fetchall()
        return result 

    

    def PartyName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name FROM public."Login" WHERE profile = "Party"; ')
                result = cursor.fetchall()
                db.commit()
               
                return result

    def CheckPartyExist(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
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
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
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
        if allowed_file(self.logo.filename):
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute('INSERT INTO public."Party" ("Party_name", "Manifesto", "Logo") VALUES (%s, %s, %s)', (self.party, self.manifesto, self.logo.filename, ))
                    db.commit()
            return True
        
        else:
            return False
        

    def updateProfileParty(self):
        print(self.manifesto)
        print((self.logo))
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:     
                if self.manifesto and self.logo.filename != "":
                    cursor.execute('UPDATE public."Party" set "Logo" = %s AND "Manifesto" = %s WHERE "Party_name" = %s', (self.logo.filename, self.manifesto, self.party, ))
                    db.commit()
                    self.uploadImagePartyLogo()
                elif self.manifesto == "" and self.logo.filename != "": 
                    cursor.execute('UPDATE public."Party" set "Logo" = %s WHERE "Party_name" = %s', (self.logo.filename, self.party, ))
                    db.commit()
                    self.uploadImagePartyLogo()
                elif self.logo.filename == "" and self.manifesto !="": 
                    cursor.execute('UPDATE public."Party" set "Manifesto" = %s WHERE "Party_name" = %s', (self.manifesto, self.party, ))
                    db.commit()
                else:
                    return
     

    def creatNewDistrictProfile(self):
        #print("here")
        #print(self.nric)
        #print(self.name)
        #print(self.image)

        existing_candidate = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                #check if candidate is already registered
                for i in range(len(self.nric)):
                    nric = self.nric[i]
                    #print(f"nric: {nric}")
                    #print((type(self.candidate_list)[i]))
                    cursor.execute('SELECT * FROM public."Candidate" WHERE "NRIC" = %s ;',(nric,))
                    #cursor.execute('SELECT * FROM "Candidate" limit 0')
                    #colnames = [desc[0] for desc in cursor.description]
                    #print(colnames)
                    candidate = cursor.fetchone()
                    #print(f"in class: {candidate}")
                    
                    if candidate == None:
                        continue
                
                    else:
                        existing_candidate.append(candidate)

        #insert candidates to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                if len(existing_candidate) == 0:
                    for i in range(len(self.nric)):
                        nric = self.nric[i]
                        name = self.name[i]
                        image = self.image[i].filename
                        cursor.execute('INSERT INTO public."Candidate" ("NRIC", "Name", "Image", "Party_name", "DistrictName") VALUES (%s, %s, %s, %s, %s)', (nric, name, image, self.partyName, self.districtName, ))
                        db.commit()

                else:
                    return existing_candidate, False
            
        return existing_candidate, True


    def getCandidates(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."Candidate" WHERE "Party_name" = %s AND "DistrictName" = %s', (self.party, self.districtName, ))
                result = cursor.fetchall()
                print(result)
        return result

    def updateNewDistrictProfile(self):
        print(self.Oldnric)
        print(self.Oldname)

        print(self.nric)
        print(self.name)
        print(self.image)

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for i in range(5):
                    if self.image[i].filename != "":
                        cursor.execute('UPDATE public."Candidate" SET "Image" = %s WHERE "NRIC" = %s AND "Name" = %s',(self.image[i].filename, self.Oldnric[i], self.Oldname[i],))

                    if self.name[i] != "":
                        cursor.execute('UPDATE public."Candidate" SET "Name" = %s WHERE "Name" = %s AND "NRIC" = %s',(self.name[i], self.Oldname[i], self.Oldnric[i],))

                    if self.nric[i] != "":
                        cursor.execute('UPDATE public."Candidate" SET "NRIC" = %s WHERE "NRIC" = %s',(self.nric[i], self.Oldnric[i],))
                db.commit() 

    def load_image(self, filepath: str) -> bytes:
        image = Image.open(filepath)  # any image
        l = np.array(image.getdata())

        # To transform an array into image using PIL:
        #channels = l.size // (image.height * image.width)
        l = l.reshape(image.height, image.width).astype(
            "uint8"
        )  # unit8 is necessary to convert 
        im = Image.fromarray(l).convert('RGB')

        # to transform the image into bytes:
        with io.BytesIO() as output:
            im.save(output, format="PNG")
            contents = output.getvalue()
        return contents 

### voter Use case ###
class VoterPage:
    def __init__(self) -> None:
        self.controller = VoterPageController()
        
    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]
        if self.button_id == "b1":
            print("test")
            return redirect(url_for("voterUpdateAddress"))
        elif self.button_id =='return':
            return redirect(url_for("index"))

    def voterTemplate(self, username):
        return render_template("voterHome.html", username=username)

    def voterTemplateUpdateAddress(self, username, address_postalCode):
        return render_template("voterUpdateAddress.html", username=username, address_postalCode=address_postalCode)
""" class VoterPageController:
    def __init__(self) -> None:
        self.entity = VoterDetails()

    def getName(self):
        return self.entity.voterGetName()

    def getPhoneNumber(self):
        return self.entity.phone_number()

    def getAddress(self):
        return self.entity.voterGetAddress()

    def setAddress(self, request):
        streetName = str(request["streetName"]).split(" ")
        #streetName.remove("Singapore")
        streetName = streetName[:-2]
        self.entity.address = " ".join(streetName) + " " + str(request["unitNumber"])
        self.entity.postalCode = str(request["postalCode"])
        return self.entity.voterNewAddress()
 """
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
            return redirect(url_for("voterUpdatePhoneNumber"))
        elif self.button_id =='return':
            return redirect(url_for("index"))


    def voterTemplate(self, username, details, constituency):
        return render_template("voterHome.html", username=username, details=details, constituency=constituency)

    def voterTemplateUpdateAddress(self, username):
        return render_template("voterUpdateAddress.html", username=username)

    def voterTemplateUpdatePhoneNumber(self, username):
        return render_template("voterUpdatePhoneNumber.html", username=username)

    def voterTemplateViewParties(self, username, parties):
        return render_template("voterViewParties.html", username=username, parties=parties)
    
    def voterTemplateViewCandidates(self, username, parties, candidates):
        return render_template("voterViewCandidates.html", username=username, parties=parties, candidates=candidates)

    
class VoterPageController:
    def __init__(self) -> None:
        self.entity = VoterDetails()

    def getName(self):
        return self.entity.voterGetName()

    def getPhoneNumber(self):
        return self.entity.voterGetPhoneNumber()

    def getAddress(self):
        return self.entity.voterGetAddress()

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

class VoterDetails:
    def voterDetails(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name, address, postal_code, phone_number FROM public."Voter" WHERE nric = %s; ', (session["username"],))
                result = cursor.fetchall()
                db.commit()
                return result[0]

    def voterGetName(self) -> str:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name FROM public."Voter" WHERE nric = %s; ', (session["username"],))
                result = cursor.fetchall()
                db.commit()
                return result[0][0]
    
    def voterGetAddress(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT address, postal_code FROM public."Voter" WHERE nric = %s; ', (session["username"],))
                result = cursor.fetchall()
                db.commit()
                return result[0]

    def voterGetPhoneNumber(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT phone_number FROM public."Voter" WHERE nric = %s; ', (session["username"],))
                result = cursor.fetchone()
                db.commit()
                return result[0]

    def voterNewAddress(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                print("testing")
                url = f"https://www.parliament.gov.sg/mps/find-mps-in-my-constituency?SearchKeyword={self.postal_code}"
                fp = requests.get(url).text
                soup = BeautifulSoup(fp, 'html.parser')
                contestingZone = soup.find("div" , {"class" : "row result-grc result-pd"}).find("h4").find("a").text
                cursor.execute(f'UPDATE public."Voter" SET address = %s , postal_code = %s, "contestingZone" = %s WHERE nric = %s; ', (self.address, self.postal_code, contestingZone , session["username"],))
                db.commit()
    
    def voterNewPhoneNumber(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'UPDATE public."Voter" SET phone_number = %s WHERE nric = %s; ', (self.phone_number, session["username"],))
                db.commit()
                print("testing")

    def voterDistrictName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "contestingZone" FROM public."Voter" WHERE nric = %s;', (session["username"],))
                result = cursor.fetchone()
                return result[0]

    def voterGetCandidatesByDistrict(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Name", "Image", "Party_name" FROM public."Candidate" WHERE "DistrictName" = %s AND "Party_name" = %s;', (self.districtName,self.chosen_party))
                result = cursor.fetchall()
                print(result)
                return result

    def voterGetParties(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT "Party_name", "Manifesto" FROM public."Party";')
                result = cursor.fetchall()
                return result

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
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                result = cursor.fetchall()
                db.commit()
                return result

    def deleteAdmin(self,username):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'DELETE from public."Login" where profile = %s AND username = %s;',('admin',username,))
                db.commit()
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                
                db.commit()
                result = cursor.fetchall()
                return result

    def createAdmin(self,admin_username,admin_password,admin_name):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'INSERT INTO public."Login"(username,password,name,profile) VALUES(%s,%s,%s,%s);',(admin_username,admin_password,admin_name,'admin',))
                db.commit()
                cursor.execute(f'SELECT username,password,name FROM public."Login" where profile=%s;',('admin',))
                db.commit()
                result = cursor.fetchall()
                return result
"""
class UserAccount:
    def getAllProfiles(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()
        return profiles

    def getUsernameProfiles(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, profile FROM users")
                profiles = cursor.fetchall()
        return profiles

    def doesUserExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (self.username, self.password, self.account_type))
                result = cursor.fetchone()
                db.commit()

                if result != None: return True
                else: return False

    def getDatabyUandT(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                    db.commit()
                    return cursor.fetchall()

    def getDatabyU(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"SELECT username, password, profile FROM users WHERE username='{self.username}'")
                    db.commit()
                    return cursor.fetchall()

    def createAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result == None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"INSERT INTO users (profile, username, password) VALUES (%s, %s, %s)", (self.account_type, self.username, self.password))
                            db.commit()
                    return True
                else:
                    return False

    def editAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"UPDATE users SET username=%s, password=%s, profile=%s WHERE username=%s AND profile=%s", (self.new_username, self.new_password, self.new_account_type, self.username, self.account_type))
                        db.commit()
                    return True
                else:
                    return False

    def viewAccount(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                db.commit()
                return cursor.fetchall()

    def searchAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username='{self.username}'")
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def suspendAccount(self) -> bool:
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"DELETE FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                        db.commit()
                    return True
                else:
                    return False

### Use Case 2 (LOGOUT) ###
class Logout:
    def __init__(self, session) -> None:
        self.session = session
        self.username = session["username"]
        self.controller = LogoutController(self.session, self.username)

    def logUserOut(self):
        self.session = self.controller.editSession(self.session, self.username)
        flash(f"{self.username} logged out!")
        return redirect(url_for("index"))

class LogoutController:
    def __init__(self, session, username) -> None:
        self.session = session
        self.username = session["username"]
        self.entity = UserSession()

    def editSession(self, session, username):
        return self.entity.checkUserInSession(session, username)


class UserSession:
    def checkUserInSession(self, session, username):
        self.session = session
        if "username" in session and session["username"] == username:
            return self.removeUserSession(username)

    def removeUserSession(self, username):
        self.session.pop("username")
        return self.session

##################################
class UserProfile:
    def getFunctions(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT Column_name FROM Information_schema.columns WHERE Table_name like 'profile'")
                profile_function = cursor.fetchall()
                del profile_function[0]
                print(profile_function[0])
        return profile_function

    def allProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profile_name = cursor.fetchall()
        return profile_name

    def getProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM profile WHERE profile_name='{self.profile_name}'")
                db.commit()
                return cursor.fetchall()

    def createProfile(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result == None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"INSERT INTO profile (profile_name, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon) VALUES (%s, %s, %s, %s, %s, %s)", (self.profile_name, self.statistics, self.cart, self.accounts, self.menu, self.coupon))
                            db.commit()
                    return True
                else:
                    return False

    def editProfile(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"UPDATE profile SET profile_name=%s, grant_view_statistics=%s, grant_view_edit_cart=%s, grant_view_edit_accounts=%s, grant_view_edit_menu=%s, grant_view_edit_coupon=%s WHERE profile_name=%s", (self.new_profile_name, self.statistics, self.cart, self.accounts, self.menu, self.coupon, self.profile_name))
                            db.commit()
                    return True
                else:
                    return False

    def viewProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM profile WHERE profile_name='{self.profile_name}'")
                db.commit()
                return cursor.fetchall()

    def searchProfile(self) -> bool:
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def suspendProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"DELETE FROM profile WHERE profile_name='{self.profile_name}'")
                            db.commit()
                    return True
                else:
                    return False
"""
