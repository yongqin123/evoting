from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from app import db
from models import *


admin = Blueprint('admin', __name__, template_folder='templates')


@admin.route('/view_party')
def view_party():
    parties = Party.query.all()
    election_areas = ElectionArea.query.all()
    return render_template("admin/party.html", parties = parties, election_areas = election_areas)


@admin.route('/insert_party', methods = ['POST'])
def insert_party():
    if request.method == 'POST':
        title = request.form['title']
        manifesto = request.form['manifesto']
        logo = request.form['logo']
        participating = request.form.getlist('participating')
        party = Party(title, manifesto, logo)

        for id in participating:
            election_area = ElectionArea.query.get(id)
            party.participating.append(election_area)

        db.session.add(party)
        db.session.commit()

        flash("Party added successfully.")
        return redirect(url_for('admin.view_party'))


@admin.route('/update_party', methods = ['GET','POST'])
def update_party():
    if request.method == 'POST':
        party = Party.query.get(request.form.get('id'))
        party.title = request.form['title']
        party.manifesto = request.form['manifesto']
        party.logo = request.form['logo']
        party.participating = []
        participating = request.form.getlist('participating')

        for id in participating:
            election_area = ElectionArea.query.get(id)
            party.participating.append(election_area)
        
        db.session.commit()

        flash("Party updated successfully.")
        return redirect(url_for('admin.view_party'))


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
        election_area = ElectionArea.query.get(request.form.get('id'))
        election_area.title = request.form['title']
        election_area.description = request.form['description']

        db.session.commit()

        flash("Election area updated successfully.")
        return redirect(url_for('admin.view_election_area'))


@admin.route('/delete_election_area/<id>', methods = ['GET','POST'])
def delete_election_area(id):
    election_area = ElectionArea.query.get(id)
    db.session.delete(election_area)
    db.session.commit()
    flash("Election area deleted successfully.")
    return redirect(url_for('admin.view_election_area'))