#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import( 
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for,
  jsonify
  )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']='postgres://postgres:123@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#







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
  areas=Venue.query.distinct(Venue.city,Venue.state).all()
  data=[]
  for area in areas:
    city=area.city
    state=area.state
    venues=Venue.query.filter(Venue.city==area.city,Venue.state==area.state).all()
    venues_lists=[]
    for venue in venues:
      id=venue.id
      name=venue.name
      shows=venue.show
      current_time=datetime.now()
      num_upcoming_shows=0
      for show in shows:
        if show.start_time > current_time:
          num_upcoming_shows+=1
      venues_lists.append({
        "id":id,
        "name":name,
        "num_upcoming_shows":num_upcoming_shows
      })
    data.append({
      "city":city,
      "state":state,
      "venues":venues_lists
    })      
     


  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_word=request.form.get('search_term')
  result=Venue.query.filter(Venue.name.ilike('%{}%'.format(search_word))).all()
  response={
    "count":len(result),
    "data":result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  past_shows=db.session.query(Artist,Show).join(Show).join(Venue).\
    filter(
      Show.Venue_id == Venue.id,
      Show.Artist_id == Artist.id,
      Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows=db.session.query(Artist,Show).join(Show).join(Venue).\
    filter(
      Show.Venue_id == Venue.id,
      Show.Artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
    all()
  
  venue=Venue.query.get(venue_id)
  
  data=venue.__dict__
 
        
  data['past_shows']= [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows]

  data['upcoming_shows']=[{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows]

  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']= len(upcoming_shows)
    

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    address=request.form['address']
    phone=request.form['phone']
    facebook_link=request.form['facebook_link']
    genres=request.form.getlist('genres')
    genres=','.join(genres)
    seeking_description=request.form['seeking_description']
    website=request.form['website']
    if request.form['seeking_talent'].lower() == 'true':
      seeking_talent=True
    else: 
      seeking_talent=False  
    image_link=request.form['image_link']
    venue=Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=facebook_link,seeking_description=seeking_description,seeking_talent=seeking_talent,website=website,genres=genres)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:  
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  finally:
    db.session.close() 
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
 
  return render_template('pages/artists.html', artists=Artist.query.order_by('id').all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_word=request.form.get('search_term')
    result=Artist.query.filter(Artist.name.ilike('%{}%'.format(search_word))).all()
    response={
      "count":len(result),
      "data":result
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  #data=db.session.query(Artist).join(Show).filter(Show.Artist_id==artist_id).all()
  
  past_shows=db.session.query(Venue,Show).join(Show).join(Artist).\
    filter(
      Show.Venue_id == Venue.id,
      Show.Artist_id == Artist.id,
      Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows=db.session.query(Venue,Show).join(Show).join(Artist).\
    filter(
      Show.Venue_id == Venue.id,
      Show.Artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
    all()
  
  artist=Artist.query.get(artist_id)
  
  data=artist.__dict__
 
        
  data['past_shows']= [{
            'artist_id': venue.id,
            "artist_name": venue.name,
            "artist_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows]

  data['upcoming_shows']=[{
            'artist_id': venue.id,
            'artist_name': venue.name,
            'artist_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows]

  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']= len(upcoming_shows)
  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist=Artist.query.get(artist_id)
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    genres=request.form.getlist('genres')
    artist.genres=','.join(genres)
    artist.facebook_link=request.form['facebook_link']
    if request.form['seeking_venue'].lower() == 'true':
      artist.seeking_venue=True
    else:
      artist.seeking_venue=False  
    artist.seeking_description=request.form['seeking_description']
    artist.website=request.form['website']
    artist.image_link=request.form['image_link']
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    venue=Venue.query.get(venue_id)
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    genres=request.form.getlist('genres')
    venue.genres=','.join(genres)
    venue.facebook_link=request.form['facebook_link']
    venue.website=request.form['website']
    venue.image_link=request.form['image_link']
    venue.seeking_description=request.form['seeking_description']
    if request.form['seeking_talent'].lower() == 'true':
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False  
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()    
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name=request.form['name']
  city=request.form['city']
  state=request.form['city']
  phone=request.form['phone']
  genres=request.form.getlist('genres')
  genres=','.join(genres)
  facebook_link=request.form['facebook_link']
  seeking_description=request.form['seeking_description']
  if request.form['seeking_venue'].lower() == 'true':
    seeking_venue=True
  else:
    seeking_venue=False  
  website=request.form['website']
  try:
    artist=Artist(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,seeking_description=seeking_description,seeking_venue=seeking_venue,website=website)
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows=Show.query.all()
  for show in shows:
    data.append({
      "venue_id":show.venue.id,
      "venue_name":show.venue.name,
      "artist_id":show.artist.id,
      "artist_name":show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
    try:
        show=Show(Artist_id=int(request.form['artist_id']),Venue_id=int(request.form['venue_id']),start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
      # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        flash('An error occurred. Show could not be listed.')
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
