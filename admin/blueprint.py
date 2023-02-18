from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from app import db
from models import *


admin = Blueprint('admin', __name__, template_folder='templates')

@admin.route('/manage_election', methods = ['POST','GET'])
def manage_election():
    
    if request.method == 'POST':
        print("In POST")
        print()
        if request.form["button_manage"] == "button_add_election":
            print("In Post")
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            status = "Open"
            elections = Elections(title, description, start_date,end_date,status)

            db.session.add(elections)
            db.session.commit()

            flash("Election added successfully.")
     
        if request.form["button_manage"] == "button_close":
            print("Inside close")
            if(request.form['status'] == "Close"):
                flash("Election already closed for: " + request.form['title'])
            else:
                election = Elections.query.get(request.form['title'])
                election.status = "Close"
                db.session.commit()
                flash("Election CLOSED for: " + request.form['title'])
            """
            title = request.form['title']
            description = request.form['desc']
            sdate = request.form['sdate']
            edate = request.form['edate']
            status = "Close"
            """
            
            
        if request.form["button_manage"] == "button_delete":
            election = Elections.query.get(request.form['title'])
            status = request.form['status']
            if(status == "Open"):
                flash(request.form['title'] + " NOT delete, election is still ongoing.")
            else:
            
                db.session.delete(election)
                db.session.commit()
                flash("Election for: " + request.form['title'] + " deleted successfully.")

        if request.form["button_manage"] == "button_decrypt":
            if(request.form['status'] == "Open" or request.form['status'] == 'Ended'):
                flash("Election have not ended for: " + request.form['title'] + ", you may not decrypt now.")
            else:
                print("do your code here")
                return redirect(url_for("adminDecrypt"))

    if request.method == 'GET':
        print("get")

    elections = Elections.query.all()
    parties = Party.query.all()
    election_areas = ElectionArea.query.all()
    
    return render_template("admin/manage_election.html", elections=elections, parties=parties,election_areas=election_areas)

@admin.route('/view_party')
def view_party():
    parties = Party.query.all()
    election_areas = ElectionArea.query.all()
    return render_template("admin/party.html", parties = parties, election_areas = election_areas)


@admin.route('/insert_party', methods = ['POST'])
def insert_party():
    if request.method == 'POST':
        title = request.form['title']
        username = request.form['username']
        password = request.form['password']
        participating = request.form.getlist('participating')
        party = Party(title, username, password)
        print("Printing participating election")
        print(participating)
        print(ElectionArea.query.get(title))
        for title in participating:
            
            print(title)
            election_area = ElectionArea.query.get(title)
            #election_area = ElectionArea.query.filter(id).first()
            print(type(election_area))
            party.participating.append(election_area)
     
        db.session.add(party)
        db.session.commit()

        flash("Party added successfully.")
        return redirect(url_for('admin.view_party'))


@admin.route('/update_party', methods = ['GET','POST'])
def update_party():
    if request.method == 'POST':
        print(request.form)
        title = request.form['title']
        print(title)
        #title = request.form['title']
        party = Party.query.get(title)
        print(party)
        if party is None:
            return "Party not found", 404
        party.username = request.form['username']
        party.password = request.form['password']
        party.participating = []
        participating = request.form.getlist('participating')
        print("Printing participating")
        print(participating)
        for title in participating:
            print("Hello")
            print("Printing title: " + title)
            election_area = ElectionArea.query.filter_by(title=title).first()
            party.participating.append(election_area)

        db.session.commit()

        flash("Party updated successfully.")
        return redirect(url_for('admin.view_party'))
    # Save the changes to the database
    db.session.commit()

    # Return a response to the user
    return "Party updated successfully"

@admin.route('/delete_party/<id>', methods = ['GET','POST'])
def delete_party(id):
    party = Party.query.get(id)
    db.session.delete(party)
    db.session.commit()
    flash("Party deleted successfully.")
    return redirect(url_for('admin.view_party'))


@admin.route('/view_election_area')
def view_election_area():
    election_areas = ElectionArea.query.all()
    return render_template("admin/election_area.html", election_areas = election_areas)


@admin.route('/insert_election_area', methods = ['POST'])
def insert_election_area():
    if request.method == 'POST':
        
        title = request.form['title']
        description = request.form['description']
        election_area = ElectionArea(title, description)

        db.session.add(election_area)
        db.session.commit()

        flash("Election area added successfully.")
        return redirect(url_for('admin.view_election_area'))


@admin.route('/update_election_area', methods = ['GET','POST'])
def update_election_area():
    if request.method == 'POST':
        election_area = ElectionArea.query.get(request.form['title'])
        
        print("PRintign election_are")
        print(election_area)
        #print("Trying to get id")
        #print(request.form['id'])
        #election_area.id = request.form['id']
        #election_area.title = request.form['title']
        #election_area.title = request.form['title']
        election_area.description = request.form['description']
        
        db.session.commit()

        flash("Election area updated successfully.")
        return redirect(url_for('admin.view_election_area'))


@admin.route('/delete_election_area/<title>', methods = ['GET','POST'])
def delete_election_area(title):
    election_area = ElectionArea.query.get(title)
    db.session.delete(election_area)
    db.session.commit()
    flash("Election area deleted successfully.")
    return redirect(url_for('admin.view_election_area'))