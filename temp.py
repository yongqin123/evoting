from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "e_voting"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:csci321voting@evoting.chzmr6u2ohlt.ap-southeast-1.rds.amazonaws.com/voting'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

party_election_area = db.Table(
    'party_election_area',
    db.Column('party_id', db.Integer, db.ForeignKey('party.id')),
    db.Column('election_area_id', db.Integer, db.ForeignKey('election_area.id'))
)

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    manifesto = db.Column(db.String(100))
    logo = db.Column(db.String(100))
    participating = db.relationship('ElectionArea', secondary=party_election_area, backref='participants')

    def __init__(self, title, manifesto, logo):
        self.title = title
        self.manifesto = manifesto
        self.logo = logo

class ElectionArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

if __name__ == "__main__":
    app.run(debug=True)