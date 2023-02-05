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
        if request.form["button_type"] == "button_delete":
            username = request.form["username"]
            data = boundary.controller.delete_admin(username)
            print("In post")
            return redirect(url_for('index', data=data))
        if request.form["button_type"] == "button_create":
            a_username = request.form["admin_username"]
            a_password = request.form["admin_password"]
            a_name = request.form["admin_name"]
            data = boundary.controller.createAdmin(a_username,a_password,a_name)
            return redirect(url_for('index',data=data))
        

### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True)

