from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # Max Url length may range upto 2048 characters
    # Reference: Alembic Column change detect ON
    #            https://peterspython.com/en/blog/make-alembic-detect-column-type-changes-and-change-the-length-of-string-fields
    image_link = db.Column(db.String(2048), 
                           default="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
                          )
    facebook_link = db.Column(db.String(2048))
    # TODO:[COMPLETED] implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(2048))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(256), nullable=True)



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # Using array to store multiple values of genres
    genres = db.Column(db.ARRAY(db.String()))
    # Max url length may range upto 2048 characters
    image_link = db.Column(db.String(2048),
                           default="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
                          )
    facebook_link = db.Column(db.String(2048))
    # TODO:[COMPLETED] implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(2048))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(256), nullable=True)



# TODO:[COMPLETED] Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    # Relationships
    # Reference : https://stackoverflow.com/questions/44538911/flask-sqlalchemy-backref-function-and-backref-parameter
    #             https://docs.sqlalchemy.org/en/13/orm/backref.html
    #             https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
    artist = db.relationship('Artist', backref=db.backref("shows", cascade="all,delete-orphan", lazy=True), lazy=True)
    venue = db.relationship('Venue', backref=db.backref("shows", cascade="all,delete-orphan", lazy=True), lazy=True)
