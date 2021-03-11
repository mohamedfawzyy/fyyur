from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    artist=db.relationship('Venue',secondary='Show')
    show=db.relationship('Show',backref='venue')



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    
    venue=db.relationship('Artist',secondary='Show')
    show=db.relationship('Show',backref='artist')

class Show(db.Model):
  __tablename__='Show'
  id=db.Column(db.Integer,primary_key=True)
  Artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  Venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  start_time=db.Column(db.DateTime,nullable=False)
