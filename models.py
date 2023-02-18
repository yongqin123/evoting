from app import db

PartyElectionArea = db.Table(
    'PartyElectionArea',
    db.Column('party_title', db.Text, db.ForeignKey('Party.title')),
    db.Column('election_title', db.Text, db.ForeignKey('ContestingZone.title'))
)
class Party(db.Model):
    __tablename__ = 'Party'
    #id = db.Column(db.Integer)
    title = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    participating = db.relationship('ElectionArea', secondary=PartyElectionArea, backref='participants')

    def __init__(self, title, username, password):
        self.title = title
        self.username = username
        self.password = password

class ElectionArea(db.Model):
    __tablename__ = 'ContestingZone'
    #id = db.Column(db.Integer)
    title = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

class Elections(db.Model):
    __tablename__ = 'Election'
    #column_not_exist_in_db = db.Column(db.Integer, primary_key=True) # just add for sake of this error, dont add in db
    title = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(100))

    def __init__(self, title,description, start_date, end_date,status):
        self.title = title
        self.start_date=start_date
        self.end_date=end_date
        self.description = description
        self.status=status




