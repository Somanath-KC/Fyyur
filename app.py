#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    abort, 
    jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Initalizing app with db
db.init_app(app) 


# TODO:[COMPLETED] connect to a local postgresql database
# db Connection URI Specified in config.py

# Integrating Flask Migrations to this application
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# All models were placed in a separate file models.py.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # parses the input values only if input value is string type.
  # if value is str type the value will be parsed to datetime object.
  if type(value) == type(" "):
      date = dateutil.parser.parse(value)
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO:[COMPLETED] replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  data = []

  count_feild = db.func.count(Venue.city)
  cities_states = db.session.query(Venue.city, Venue.state, count_feild).group_by(Venue.city, Venue.state).order_by(count_feild).all()
  

  for item in cities_states[::-1]:
    city_info = {
        "city": item.city,
        "state": item.state,
        "venues" :[]
      }

    # Query to get all the venues from each city 
    venues = Venue.query.filter(Venue.city==item.city, Venue.state == item.state).all()

    # Grab all info from each info
    for venue in venues:
      city_info['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.datetime > datetime.now()).count()
          })
    data.append(city_info)

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: [COMPLETED] implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  # ilike is used to look for case-insensitive string pattern
  # '%{}%' pattern looks in db column string containing for input string at any position
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"count": len(data), "data": data }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO:[COMPLETED] replace with real venue data from the venues table, using venue_id
  
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

  # Query Venue data
  data = Venue.query.get(venue_id)

  # if venue id is not found 404 error will be sent.
  if not data:
    abort(404)

  # Query all list of past shows
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.datetime < datetime.now()).all()
  past_shows_count = len(past_shows)

  # Query all list of upcoming shows
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.datetime > datetime.now()).all()
  upcoming_shows_count = len(upcoming_shows)


  data.past_shows = past_shows
  data.past_shows_count = past_shows_count
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = upcoming_shows_count

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO:[COMPLETED] insert form data as a new Venue record in the db, instead
  # TODO:[COMPLETED] modify data to be the data object returned from db insertion

  form_data = request.form
  venue_form = VenueForm(meta={'csrf': False})
  
  if not venue_form.validate_on_submit():
    # Flashes all error messages to user
    for error in venue_form.errors.keys():
      flash('Validation error at '+ error, 'alert-warning')
    
    # This avoids user from re-entering the values for form.
    return render_template('forms/new_venue.html', form=venue_form)

  try:
    # Assiging attributes using python dict
    # Refrence: https://codereview.stackexchange.com/questions/171107/python-class-initialize-with-dict
    new_venue = Venue(**venue_form.data)
    db.session.add(new_venue)
    db.session.commit()
    # Flash on successful db insert
    flash('Venue ' + new_venue.name + ' listed succesfully', 'alert-success')
  except Exception as e:
    # Print Exception message for debugging
    print(e)
    db.session.rollback()
    # TODO:[COMPLETED] on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Error in creating venue ' + form_data.get('name'), 'alert-danger')
  finally:
    db.session.close()
 
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO:[COMPLETED] Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE:[COMPLETED] Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  venue = Venue.query.get(venue_id)
  error_flag = False

  try:
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    # Print Exception message for debugging
    print(e)
    db.session.rollback()
    error_flag = True
  finally:
    db.session.close()

  if error_flag:
    return jsonify({'status': 'error'})
  else:
    return jsonify({'status': 'ok'})


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

  artist = Artist.query.get(artist_id)
  error_flag = False

  try:
    db.session.delete(artist)
    db.session.commit()
  except Exception as e:
    # Print Exception message for debugging
    print(e)
    db.session.rollback()
    error_flag = True
  finally:
    db.session.close()

  if error_flag:
    return jsonify({'status': 'error'})
  else:
    return jsonify({'status': 'ok'})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO:[COMPLETED] replace with real data returned from querying the database
  #  data=[{
  #    "id": 4,
  #    "name": "Guns N Petals",
  #  }, {
  #    "id": 5,
  #    "name": "Matt Quevedo",
  #  }, {
  #    "id": 6,
  #    "name": "The Wild Sax Band",
  #  }]

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO:[COMPLETED] implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  # ilike is used to look for case-insensitive string pattern
  # '%{}%' pattern looks in db column string containing for input string at any position
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"count": len(data), "data": data }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO:[COMPLETED] replace with real venue data from the venues table, using venue_id

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

  # Query Venue data
  data = Artist.query.get(artist_id)

  # if venue id is not found 404 error will be sent.
  if not data:
    abort(404)

  # Query all list of past shows
  past_shows = Show.query.filter(Show.artist_id == artist_id, Show.datetime < datetime.now()).all()
  past_shows_count = len(past_shows)

  # Query all list of upcoming shows
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.datetime > datetime.now()).all()
  upcoming_shows_count = len(upcoming_shows)


  data.past_shows = past_shows
  data.past_shows_count = past_shows_count
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = upcoming_shows_count

  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  # TODO:[COMPLETED] populate form with fields from artist with ID <artist_id>
  artist_item = Artist.query.get(artist_id)

  if not artist_item:
    abort(404)

  artist={
    "id": artist_item.id,
    "name": artist_item.name,
    "genres": artist_item.genres,
    "city": artist_item.city,
    "state": artist_item.state,
    "phone": artist_item.phone,
    "website": artist_item.website,
    "facebook_link": artist_item.facebook_link,
    "seeking_venue": artist_item.seeking_venue,
    "seeking_description": artist_item.seeking_description,
    "image_link": artist_item.image_link
  }

  form = ArtistForm(**artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO:[COMPLETED] take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(meta={'csrf': False})

  if not form.validate_on_submit():
    # Flashes all error messages to user
    for error in form.errors.keys():
      flash('Validation error at '+ error, 'alert-warning')
    
    # This avoids user from re-entering the values for form.
    return redirect(url_for('edit_artist', artist_id=artist_id))

  # Modifing the Venue that exists in the DB
  artist = Artist.query.get(artist_id)

  try:
    artist.name = form.name.data 
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.genres = form.genres.data
    artist.website = form.website.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!', 'alert-success')
  except Exception as e:
    db.session.rollback()
    # Print exception message for debugging
    print(e)
    flash('Something went wrong when updating the artist ' + artist.name, 'alert-danger')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }

  # TODO:[COMPLETED] populate form with values from venue with ID <venue_id>
  venue_item = Venue.query.get(venue_id)

  if not venue_item:
    abort(404)

  venue={
    "id": venue_item.id,
    "name": venue_item.name,
    "genres": venue_item.genres,
    "address": venue_item.address,
    "city": venue_item.city,
    "state": venue_item.state,
    "phone": venue_item.phone,
    "website": venue_item.website,
    "facebook_link": venue_item.facebook_link,
    "seeking_talent": venue_item.seeking_talent,
    "seeking_description": venue_item.seeking_description,
    "image_link": venue_item.image_link
  }

  form = VenueForm(**venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO:[COMPLETED] take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(meta={'csrf': False})

  if not form.validate_on_submit():
    # Flashes all error messages to user
    for error in form.errors.keys():
      flash('Validation error at '+ error, 'alert-warning')
    
    # This avoids user from re-entering the values for form.
    return redirect(url_for('edit_venue', venue_id=venue_id))

  # Modifing the Venue that exists in the DB
  venue = Venue.query.get(venue_id)

  try:
    venue.name = form.name.data 
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.genres = form.genres.data
    venue.website = form.website.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!', 'alert-success')
  except Exception as e:
    db.session.rollback()
    # Print exception message for debugging
    print(e)
    flash('Something went wrong when updating the venue ' + venue.name, 'alert-danger')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO:[COMPLETED] insert form data as a new Venue record in the db, instead
  # TODO:[COMPLETED] modify data to be the data object returned from db insertion

  form_data = request.form
  artist_form = ArtistForm(meta={'csrf': False})

  if not artist_form.validate_on_submit():
    # Flashes all error messages to user
    for error in artist_form.errors.keys():
      flash('Validation error at '+ error, 'alert-warning')
    
    # This avoids user from re-entering the values into form.
    return render_template('forms/new_artist.html', form=artist_form)

  try:
    # Assiging attributes using python dict
    # Refrence: https://codereview.stackexchange.com/questions/171107/python-class-initialize-with-dict
    new_artist = Artist(**artist_form.data)
    db.session.add(new_artist)
    db.session.commit()
    #  on successful db insert, flash success
    flash('Artist ' + new_artist.name + ' listed succesfully', 'alert-success')
  except Exception as e:
    # Print Exception message for debugging
    print(e)
    db.session.rollback()
    # TODO:[COMPLETED] on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Error in creating artist ' + form_data.get('name'), 'alert-danger')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO:[COMPLETED] replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  data = shows=Show.query.all()

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO:[COMPLETED] insert form data as a new Show record in the db, instead
  show_form =  ShowForm(meta={'csrf': False})
  
  if not show_form.validate_on_submit():
    for error in show_form.errors.keys():
      flash('Validation Error at '+ error, 'alert-warning')

    return render_template('forms/new_show.html', form=show_form)
  
  # Checks the seeking status of Venues and Artists
  artist_seeking_venue_status = db.session.query(Artist.seeking_venue).filter(Artist.id == show_form.artist_id.data).scalar()
  venue_seeking_talent_status = db.session.query(Venue.seeking_talent).filter(Venue.id == show_form.venue_id.data).scalar()

  if not artist_seeking_venue_status:
    flash('Artist is currently not seeking venues.', 'alert-warning')
    return render_template('forms/new_show.html', form=show_form)

  if not venue_seeking_talent_status:
    flash('Venue is currently not seeking talent.', 'alert-warning')
    return render_template('forms/new_show.html', form=show_form)

  try:
    new_show = Show(**show_form.data)
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!', 'alert-success')
  except Exception as e:
    # Printing Exceptions for debugging
    print(e)
    db.session.rollback()
    # TODO:[COMPLETED] on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.', 'alert-danger')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
