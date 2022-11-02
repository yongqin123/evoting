### IMPORTS ###
import decimal
from re import sub
from decimal import Decimal
from inspect import _void
from random import vonmisesvariate
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime

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
        default_profiles = ["candidate", "super_admin", "voter"]
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
        default_profiles = ["candidate", "super_admin", "voter"]
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

### candidate Use case ###
class CandidatePage:
    def __init__(self) -> None:
        self.controller = CandidatePageController()

    def candidateTemplate(self, username):
        return render_template("candidateHome.html", username=username)

    
class CandidatePageController:
    def __init__(self) -> None:
        self.entity = CandidateDetails()

    def getName(self):
        return self.entity.candidateName()


class CandidateDetails:

    def candidateName(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT name FROM public."Login" WHERE profile = "candidate"; ')
                result = cursor.fetchall()
                db.commit()
                return result


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

class VoterDetails:

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

    def voterNewAddress(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                print(self.address)
                print(self.postalCode)
                cursor.execute(f'UPDATE public."Voter" SET address = %s , postal_code = %s WHERE nric = %s; ', (self.address, self.postalCode, session["username"],))
                #result = cursor.fetchall()
                db.commit()
                print("testing")
                #return result[0][0]

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