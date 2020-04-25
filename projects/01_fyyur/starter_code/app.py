# ----------------------------------------------------------------------------# 
# Imports
# ----------------------------------------------------------------------------# 

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *


# ----------------------------------------------------------------------------# 
# App Config.
# ----------------------------------------------------------------------------# 

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------# 
# Filters.
# ----------------------------------------------------------------------------# 


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------# 
# Controllers.
# ----------------------------------------------------------------------------# 


@app.route('/')
def index():
    return render_template('pages/home.html')


# Venues
# ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows  
    # per venue.
    data = []

    locations = Venue.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()

    for location in locations:
        venues = Venue.query.filter(Venue.city == location[0]).filter(Venue.state == location[1]).all()
        
    data = {
        'city': location[0], 
        'state': location[1], 
        'venues': venues
    }
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure 
    # it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square 
    # Live Music & Coffee"
    # response={
    # "count": 1, 
    # "data": [{
    # "id": 2, 
    # "name": "The Dueling Pianos Bar", 
    # "num_upcoming_shows": 0, 
    # }]
    # }

    search_term = request.form.get('search_term', '')  
    venues = db.session.query(Venue).with_entities(Venue.id, Venue.name).filter(Venue.name.contains(search_term)).all()

    data = []
    for venue in venues:
        upcoming = db.session.query(Show).filter_by(venue_id=venue.id).filter(
            Show.start_time > datetime.utcnow().isoformat()).all()
        data.append({
            "id": venue.id, 
            "name": venue.name, 
            "num_upcoming_shows": len(upcoming)
        })

    response = {
        "count": len(venues), 
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    show_query = Show.query.outerjoin(Venue, Venue.id == Show.venue_id).outerjoin(
        Artist, Artist.id == Show.artist_id).filter(Show.venue_id == venue_id)
    venue_query = Venue.query.filter_by(id=venue_id).first()
    time = datetime.now()
    future_shows = show_query.filter(Show.time >= time).all()
    past_shows = show_query.filter(Show.time < time).all()
    return render_template('pages/show_venue.html', venue=venue_query, past_shows=past_shows, future_shows=future_shows)


# Create Venue
# ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        venue = Venue(name=name, city=city, state=state, address=address,
                      phone=phone, genres=genres, facebook_link=facebook_link)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be 
    # listed.') see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session 
    # commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, 
    # have it so that clicking that button delete it from the db then redirect 
    # the user to the homepage
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('venues'))


# Artists
# ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data=[{
    # "id": 4, 
    # "name": "Guns N Petals", 
    # }, {
    # "id": 5, 
    # "name": "Matt Quevedo", 
    # }, {
    # "id": 6, 
    # "name": "The Wild Sax Band", 
    # }]
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it 
    # is case-insensitive. seach for "A" should return "Guns N Petals", 
    # "Matt Quevado", and "The Wild Sax Band". search for "band" should return 
    # "The Wild Sax Band".
    # response={
    # "count": 1, 
    # "data": [{
    # "id": 4, 
    # "name": "Guns N Petals", 
    # "num_upcoming_shows": 0, 
    # }]
    # }

    search_term = request.form.get('search_term', '').capitalize()
    response = Artist.query.filter(Artist.name.contains(search_term)).all()
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1={
    # "id": 4, 
    # "name": "Guns N Petals", 
    # "genres": ["Rock n Roll"], 
    # "city": "San Francisco", 
    # "state": "CA", 
    # "phone": "326-123-5000", 
    # "website": "https://www.gunsnpetalsband.com", 
    # "facebook_link": "https://www.facebook.com/GunsNPetals", 
    # "seeking_venue": True, 
    # "seeking_description": "Looking for shows to perform at in the San 
    # Francisco Bay Area!", 
    # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80", 
    # "past_shows": [{
    # "venue_id": 1, 
    # "venue_name": "The Musical Hop", 
    # "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60", 
    # "start_time": "2019-05-21T21:30:00.000Z"
    # }], 
    # "upcoming_shows": [], 
    # "past_shows_count": 1, 
    # "upcoming_shows_count": 0, 
    # }
    # data2={
    # "id": 5, 
    # "name": "Matt Quevedo", 
    # "genres": ["Jazz"], 
    # "city": "New York", 
    # "state": "NY", 
    # "phone": "300-400-5000", 
    # "facebook_link": "https://www.facebook.com/mattquevedo923251523", 
    # "seeking_venue": False, 
    # "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80", 
    # "past_shows": [{
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80", 
    # "start_time": "2019-06-15T23:00:00.000Z"
    # }], 
    # "upcoming_shows": [], 
    # "past_shows_count": 1, 
    # "upcoming_shows_count": 0, 
    # }
    # data3={
    # "id": 6, 
    # "name": "The Wild Sax Band", 
    # "genres": ["Jazz", "Classical"], 
    # "city": "San Francisco", 
    # "state": "CA", 
    # "phone": "432-325-5432", 
    # "seeking_venue": False, 
    # "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80", 
    # "past_shows": [], 
    # "upcoming_shows": [{
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80", 
    # "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80", 
    # "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80", 
    # "start_time": "2035-04-15T20:00:00.000Z"
    # }], 
    # "past_shows_count": 0, 
    # "upcoming_shows_count": 3, 
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    # return render_template('pages/show_artist.html', artist=data)

    show_query = Show.query.outerjoin(
        Artist, Artist.id == Show.artist_id).outerjoin(Venue, Venue.id == Show.venue_id).filter(Show.artist_id == artist_id)
    artist_query = Artist.query.filter_by(id=artist_id).first()
    time = datetime.now()
    future_shows = show_query.filter(Show.time >= time).all()
    past_shows = show_query.filter(Show.time < time).all()
    return render_template('pages/show_artist.html',
                           artist=artist_query, future_shows=future_shows,
                           past_shows=past_shows)
    

# Update
# ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # artist={
    # "id": 4, 
    # "name": "Guns N Petals", 
    # "genres": ["Rock n Roll"], 
    # "city": "San Francisco", 
    # "state": "CA", 
    # "phone": "326-123-5000", 
    # "website": "https://www.gunsnpetalsband.com", 
    # "facebook_link": "https://www.facebook.com/GunsNPetals", 
    # "seeking_venue": True, 
    # "seeking_description": "Looking for shows to perform at in the San 
    # Francisco Bay Area!", 
    # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>

    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter_by(id=artist_id).first()
    try:
        artist.name = request.form.get("name")
        artist.city = request.form.get("city")
        artist.state = request.form.get("state")
        artist.phone = request.form.get("phone")
        artist.genres = request.form.getlist("genres")
        artist.facebook_link = request.form.get("facebook_link")
        db.session.commit()
        flash('Success!' + artist.name + ' has been updated.')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              artist.name + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # venue={
    # "id": 1, 
    # "name": "The Musical Hop", 
    # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"], 
    # "address": "1015 Folsom Street", 
    # "city": "San Francisco", 
    # "state": "CA", 
    # "phone": "123-123-1234", 
    # "website": "https://www.themusicalhop.com", 
    # "facebook_link": "https://www.facebook.com/TheMusicalHop", 
    # "seeking_talent": True, 
    # "seeking_description": "We are on the lookout for a local artist to play
    # every two weeks. Please call us.", 
    # "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter_by(id=venue_id).first()
    try:
        venue.name = request.form.get("name")
        venue.city = request.form.get("city")
        venue.state = request.form.get("state")
        venue.address = request.form.get("address")
        venue.phone = request.form.get("phone")
        venue.genres = request.form.getlist("genres")
        venue.facebook_link = request.form.get("facebook_link")
        db.session.commit()
        flash('Success!' + venue.name + ' has been updated.')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))


# Create Artist
# ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        artist = Artist(name=name, city=city, state=state,
                        phone=phone, genres=genres, facebook_link=facebook_link)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be
    # listed.')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


# Shows
# ----------------------------------------------------------------

@app.route('/shows')
def shows():
# displays list of shows at /shows
# TODO: replace with real venues data.
# num_shows should be aggregated based on number of upcoming shows per venue.
    # data=[{
    # "venue_id": 1, 
    # "venue_name": "The Musical Hop", 
    # "artist_id": 4, 
    # "artist_name": "Guns N Petals", 
    # "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80", 
    # "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "artist_id": 5, 
    # "artist_name": "Matt Quevedo", 
    # "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80", 
    # "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "artist_id": 6, 
    # "artist_name": "The Wild Sax Band", 
    # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80", 
    # "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "artist_id": 6, 
    # "artist_name": "The Wild Sax Band", 
    # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80", 
    # "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    # "venue_id": 3, 
    # "venue_name": "Park Square Live Music & Coffee", 
    # "artist_id": 6, 
    # "artist_name": "The Wild Sax Band", 
    # "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80", 
    # "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html',
                           shows=Show.query.outerjoin(
                               Venue, Venue.id == Show.venue_id)
                           .outerjoin(Artist, Artist.id == Show.artist_id).all())


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
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("artist_id")
        start_time = request.form.get("start_time")
        show = Show(artist_id=artist_id, venue_id=venue_id, time=start_time)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except Exception:
        db.session.rollback()
        flash('An error occurred. New show could not be listed.')
    finally:
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

# ----------------------------------------------------------------------------# 
# Launch.
# ----------------------------------------------------------------------------# 

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
'''
