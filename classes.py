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
import requests

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

### Use Case 1 (LOGIN) ###
class LoginPage:
    def __init__(self) -> None:
        self.controller = LoginPageController()
        self.user_exist = False

    def loginTemplate(self):
        # get all profiles
        profiles = self.controller.getProfiles()
        return render_template("login.html", profiles=profiles)

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
        return self.entity.doesUserExist()

    def redirectPage(account_type):
        default_profiles = ["party", "admin", "voter"]
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))
    def getProfiles(self) -> list:
        return self.entity.getAllProfiles()

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
                cursor.execute(f'SELECT * FROM public."Login" WHERE username = %s AND password = %s AND profile = %s', (self.username, self.password, self.account_type))
                result = cursor.fetchone()
                db.commit()
                print(result)
                print(self.username)
                print(self.password)
                print(self.account_type)
                if result != None: return True
                else: return False

### party Use case ###
class PartyPage:
    def __init__(self) -> None:
        self.controller = PartyPageController()

    def partyTemplate(self, username):
        return render_template("partyHome.html", username=username)

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]

        if self.button_id == "b1":
            return redirect(url_for("CreateProfile"))
        elif self.button_id == "b2":
            return redirect(url_for("partyUpdate"))
    
    def partyTemplateCreate(self):
        return render_template("partyCreate.html")

    def partyGetDistrict(self):
        return render_template("partyGetDistrict.html")
    
    def partyTemplateUpdate(self):
        return render_template("partyUpdate.html")
    
    

# Party Controller    
class PartyPageController:
    def __init__(self) -> None:
        self.entity = PartyDetails()

    def getName(self):
        return self.entity.PartyName()
    
    def createProfile(self, request, request_list) -> list:
        
        self.entity.nric=request_list("NRIC[]")
        self.entity.name=request_list("Name[]")
        self.entity.image=request_list("img[]")

        self.entity.partyName = request["PartyName"]
        self.entity.districtName = request["DistrictName"]
        return self.entity.createNewPartyProfile()
    
    def updateProfile(self, request, partyName):
        self.entity.partyName = partyName
        self.entity.districtName = request["DistrictName"]
        return self.entity.updatePartyProfile()




#Party Entity
class PartyDetails:

    def PartyName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name FROM public."Login" WHERE profile = "Party"; ')
                result = cursor.fetchall()
                db.commit()
                return result


    def updatePartyProfile(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM public."Candidate" WHERE "Party_name" = %s and "DistrictName" = %s ;',(self.party_name,self.districtName,))
                candidate_results = cursor.fetchall()
                print(candidate_results)

                return candidate_results  


    def createNewPartyProfile(self):
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
                        image = self.image[i]
                        cursor.execute('INSERT INTO public."Candidate" ("NRIC", "Name", "Image", "Party_name", "DistrictName") VALUES (%s, %s, %s, %s, %s)', (nric, name, image, self.partyName, self.districtName, ))
                        db.commit()

                else:
                    return existing_candidate, False
            
        return existing_candidate, True


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
class VoterPageController:
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
    def createAdmin(self):
        return self.entity.createAdmin()

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
