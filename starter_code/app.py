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
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from datetime import datetime
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  locations = Venue.query.all()
  
  unique_locations = set()
  for l in locations:
    unique_locations.add((l.city, l.state))

  data = []
  for ul in unique_locations:
    venues = Venue.query.filter(Venue.city==ul[0], Venue.state==ul[1])
    loc_info = {}
    loc_info["city"] = ul[0]
    loc_info["state"] = ul[1]
    loc_info["venues"] = []
    for v in venues:
      venue_info = {}
      venue_info["id"] = v.id
      venue_info["name"] = v.name
      venue_info["num_upcoming_shows"] = Show.query.filter(Show.venue_id==v.id, Show.start_time > datetime.now()).count()
      loc_info["venues"].append(venue_info)
    data.append(loc_info)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  st = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{st}%'))

  response = {}
  response['data'] = []
  for v in venues:
    venue_info = {}
    venue_info["id"] = v.id
    venue_info["name"] = v.name
    response["data"].append(venue_info)
  response['count'] = venues.count()

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = db.session.query(Show, Artist).join(Artist).join(Venue).\
    filter(Show.venue_id==venue_id, Show.start_time < datetime.now())

  upcoming_shows = db.session.query(Show, Artist).join(Artist).join(Venue).\
    filter(Show.venue_id==venue_id, Show.start_time > datetime.now())
  
  ps = []
  for s, a in past_shows:
    show_info = {}
    show_info["artist_id"] = a.id
    show_info["artist_name"] = a.name
    show_info["artist_image_link"] = a.image_link
    show_info["start_time"] = str(s.start_time)
    ps.append(show_info)
  
  us = []
  for s, a in upcoming_shows:
    show_info = {}
    show_info["artist_id"] = a.id
    show_info["artist_name"] = a.name
    show_info["artist_image_link"] = a.image_link
    show_info["start_time"] = str(s.start_time)
    us.append(show_info)
  
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": ps,
    "past_shows_count":past_shows.count(),
    "upcoming_shows": us,
    "upcoming_shows_count":upcoming_shows.count()
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form, meta={'csrf': False})

  error = False
  if form.validate():
    try:
      venue = Venue()
      form.populate_obj(venue)
      if venue.seeking_description:
        venue.seeking_talent = True
      db.session.add(venue)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append('|'.join(err) + ' for ' + field)
    flash('Errors: ' + ', '.join(message))

  return render_template('pages/home.html')

#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue_info = Venue.query.get(venue_id)
  venue = {
    "id": venue_info.id,
    "name": venue_info.name,
    "city": venue_info.city,
    "state": venue_info.state,
    "address": venue_info.address,
    "phone": venue_info.phone,
    "genres": venue_info.genres,
    "image_link": venue_info.image_link,
    "website": venue_info.website,
    "facebook_link": venue_info.facebook_link,
    "seeking_description": venue_info.seeking_description
  }
  form.name.data = venue_info.name
  form.city.data = venue_info.city
  form.state.data = venue_info.state
  form.address.data = venue_info.address
  form.phone.data = venue_info.phone
  form.genres.data = venue_info.genres
  form.image_link.data = venue_info.image_link
  form.website.data = venue_info.website
  form.facebook_link.data = venue_info.facebook_link
  form.seeking_description.data = venue_info.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form, meta={'csrf': False})

  error = False
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      form.populate_obj(venue)
      if venue.seeking_description:
        venue.seeking_talent = True
      else:
        venue.seeking_talent = False
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append('|'.join(err) + ' for ' + field)
    flash('Errors: ' + ', '.join(message))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + name + ' was successfully deleted!')
  else:
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()

  data = []
  for a in artists:
    artist_info = {}
    artist_info["id"] = a.id
    artist_info["name"] = a.name
    data.append(artist_info)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  st = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{st}%'))

  response = {}
  response['data'] = []
  count = 0
  for a in artists:
    artist_info = {}
    artist_info["id"] = a.id
    artist_info["name"] = a.name
    response["data"].append(artist_info)
    count += 1
  response['count'] = count

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = db.session.query(Show, Venue).join(Venue).join(Artist).\
    filter(Show.artist_id==artist_id, Show.start_time < datetime.now())

  upcoming_shows = db.session.query(Show, Venue).join(Venue).join(Artist).\
    filter(Show.artist_id==artist_id, Show.start_time > datetime.now())

  ps = []
  for s, v in past_shows:
    show_info = {}
    show_info["venue_id"] = v.id
    show_info["venue_name"] = v.name
    show_info["venue_image_link"] = v.image_link
    show_info["start_time"] = str(s.start_time)
    ps.append(show_info)

  us = []
  for s, v in upcoming_shows:
    show_info = {}
    show_info["venue_id"] = v.id
    show_info["venue_name"] = v.name
    show_info["venue_image_link"] = v.image_link
    show_info["start_time"] = str(s.start_time)
    us.append(show_info)

  artist = Artist.query.get(artist_id)
  data = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "genres": artist.genres,
    "image_link": artist.image_link,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "past_shows": ps,
    "past_shows_count":past_shows.count(),
    "upcoming_shows": us,
    "upcoming_shows_count":upcoming_shows.count()
  }

  return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form, meta={'csrf': False})

  error = False
  if form.validate():
    try:
      artist = Artist()
      form.populate_obj(artist)
      if artist.seeking_description:
        artist.seeking_venue = True
      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append('|'.join(err) + ' for ' + field)
    flash('Errors: ' + ', '.join(message))

  return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_info = Artist.query.get(artist_id)
  artist = {
    "id": artist_info.id,
    "name": artist_info.name,
    "city": artist_info.city,
    "state": artist_info.state,
    "phone": artist_info.phone,
    "genres": artist_info.genres,
    "image_link": artist_info.image_link,
    "website": artist_info.website,
    "facebook_link": artist_info.facebook_link,
    "seeking_description": artist_info.seeking_description
  }
  form.name.data = artist_info.name
  form.city.data = artist_info.city
  form.state.data = artist_info.state
  form.phone.data = artist_info.phone
  form.genres.data = artist_info.genres
  form.image_link.data = artist_info.image_link
  form.website.data = artist_info.website
  form.facebook_link.data = artist_info.facebook_link
  form.seeking_description.data = artist_info.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form, meta={'csrf': False})

  error = False
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)
      form.populate_obj(artist)
      if artist.seeking_description:
        artist.seeking_venue = True
      else:
        artist.seeking_venue = False
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append('|'.join(err) + ' for ' + field)
    flash('Errors: ' + ', '.join(message))

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:
    artist = Artist.query.get(artist_id)
    name = artist.name
    db.session.delete(artist)
    db.session.commit()
  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + name + ' was successfully deleted!')
  else:
    flash('An error occurred. Artist ' + name + ' could not be deleted.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  shows = Show.query.all()

  data = []
  for s in shows:
    show_info = {}
    show_info["venue_id"] = s.venue_id
    show_info["venue_name"] = s.venue.name
    show_info["artist_id"] = s.artist_id
    show_info["artist_name"] = s.artist.name
    show_info["artist_image_link"] = s.artist.image_link
    show_info["start_time"] = str(s.start_time)
    data.append(show_info)

  return render_template('pages/shows.html', shows=data)

#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form, meta={'csrf': False})
  
  error = False
  if form.validate():
    try:
      show = Show()
      form.populate_obj(show)
      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
    finally:
      db.session.close()
    if not error:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
  else:
    message = []
    for field, err in form.errors.items():
        message.append('|'.join(err) + ' for ' + field)
    flash('Errors: ' + ', '.join(message))

  return render_template('pages/home.html')

#  Error Handling
#  ----------------------------------------------------------------

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
