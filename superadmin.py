########superadmin.py###########
### MODULE IMPORTS ###
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from classes import * # import all classes from classes.py


### POSTGRESQL CONFIG ###
db_host = 'ec2-34-234-240-121.compute-1.amazonaws.com'
db_name = 'dcgsvhb0enfgfd'
db_user = 'ampoosmqdvdzte'
db_pw = '1494a152d2acffe248186b855286562322f43ab69a4ae0cd1b061bef24f36bf3'


### SESSION CONFIG (password & period) ###
app = Flask(__name__)
app.secret_key = "e_voting"
app.permanent_session_lifetime = timedelta(minutes=60)


### super admin HOMEPAGE ###
@app.route("/", methods=["GET", "POST"])
def index():
    boundary = superadminPage()
    if request.method == "GET":
        data = boundary.controller.get_admin()
        print("Super admin Home Page")
        return boundary.superadminTemplate(data) # A-B 

    elif request.method == "POST":
        print("12345")

        

### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True)

