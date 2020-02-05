#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, jsonify, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import json
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Venue
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show")

# Artist
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show")

# Show
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  all_venues = Venue.query.all()
  data = {}
  results = []
  for venue in all_venues:
    if (data.get(venue.city + venue.state) != None):
      data[venue.city + venue.state].append(venue)
    else:
      data[venue.city + venue.state] = [venue]
  for key, values in data.items():
    city = values[0].city
    state = values[0].state
    venues = []
    result = {}
    for venue in values:
      venues.append(get_venue(venue))
    result['city'] = city
    result['state'] = state
    result['venues'] = venues
    results.append(result)
    
  return render_template('pages/venues.html', areas=results)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {}
  response['count'] = len(list(results))
  response['data'] = results
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  result = Venue.query.get(venue_id)
  if (result == None):
    return render_template('errors/404.html'), 404
  if (result.genres):
    result.genres = json.loads(result.genres)
  else:
    result.genres = []
  result.past_shows = list(map(get_show_item_in_venue, filter(is_past_shows, result.shows)))
  result.upcoming_shows = list(map(get_show_item_in_venue, filter(is_upcoming_shows, result.shows)))
  result.past_shows_count = len(result.past_shows)
  result.upcoming_shows_count = len(result.upcoming_shows)
  del result.shows
  return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = json.dumps(request.form.getlist('genres'))
    facebook_link = request.form.get('facebook_link', '')

    venue = Venue(
      name=name,
      genres=genres,
      city=city,
      state=state,
      address=address,
      phone=phone,
      facebook_link=facebook_link
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    return jsonify({ 'success': False })
  else:
    return jsonify({ 'success': True, 'url': '/' })
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).with_entities(Artist.id, Artist.name).all()
  response = {}
  response['count'] = len(list(results))
  response['data'] = results
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  result = Artist.query.get(artist_id)
  if (result == None):
    return render_template('errors/404.html'), 404
  if (result.genres):
    result.genres = json.loads(result.genres)
  else:
    result.genres = []
  result.past_shows = list(map(get_show_item_in_artist, filter(is_past_shows, result.shows)))
  result.upcoming_shows = list(map(get_show_item_in_artist, filter(is_upcoming_shows, result.shows)))
  result.past_shows_count = len(result.past_shows)
  result.upcoming_shows_count = len(result.upcoming_shows)
  del result.shows
  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    id=artist.id,
    name=artist.name,
    genres=json.loads(artist.genres),
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    website=artist.website,
    facebook_link=artist.facebook_link
  )
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = json.dumps(request.form.getlist('genres'))
    artist.facebook_link = request.form.get('facebook_link', '')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(
    name=venue.name,
    genres=json.loads(venue.genres),
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    facebook_link=venue.facebook_link
  )
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = json.dumps(request.form.getlist('genres'))
    venue.facebook_link = request.form.get('facebook_link', '')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = json.dumps(request.form.getlist('genres'))
    facebook_link = request.form.get('facebook_link', '')

    artist = Artist(
      name=name,
      genres=genres,
      city=city,
      state=state,
      phone=phone,
      facebook_link=facebook_link
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    return jsonify({ 'success': False })
  else:
    return jsonify({ 'success': True, 'url': '/' })
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append(get_show_item_detail(show))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')

    show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

def is_upcoming_shows(item):
  return item.start_time > dateutil.parser.datetime.datetime.now()

def is_past_shows(item):
  return item.start_time < dateutil.parser.datetime.datetime.now()

def get_venue(item):
  venue = {}
  venue['id'] = item.id
  venue['name'] = item.name
  venue['num_upcoming_shows'] = len(list(filter(is_upcoming_shows, item.shows)))
  return venue

def get_show_item_in_venue(item):
  show = {}
  artist = Artist.query.filter(Artist.id==item.artist_id).one()
  if (artist != None):
    show['artist_name'] = artist.name
    show['artist_image_link'] = artist.image_link
  show['artist_id'] = item.artist_id
  if (item.start_time):
    show['start_time'] = item.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
  return show

def get_show_item_in_artist(item):
  show = {}
  venue = Venue.query.filter(Venue.id==item.venue_id).one()
  if (venue != None):
    show['venue_name'] = venue.name
    show['venue_image_link'] = venue.image_link
  show['venue_id'] = item.venue_id
  if (item.start_time):
    show['start_time'] = item.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
  return show

def get_show_item_detail(item):
  show = {}
  artist = Artist.query.filter(Artist.id==item.artist_id).one()
  venue = Venue.query.filter(Venue.id==item.venue_id).one()
  show['artist_id'] = item.artist_id
  show['venue_id'] = item.venue_id
  if (artist != None):
    show['artist_name'] = artist.name
    show['artist_image_link'] = artist.image_link
  if (venue != None):
    show['venue_name'] = venue.name
  if (item.start_time):
    show['start_time'] = item.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
  return show

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
