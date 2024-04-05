#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import psycopg2

# Establish connection to the database
conn = psycopg2.connect(
    host="127.0.0.1",
    dbname="fyyur",
    user="postgres",
    password="090194",
    port="5432"
)

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# Create Venue table
cur.execute("""
    CREATE TABLE IF NOT EXISTS Venue (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        city VARCHAR NOT NULL,
        state VARCHAR NOT NULL,
        num_upcoming_shows INTEGER NOT NULL
    );
""")

# Insert data into Venue table
venues_data = [
    {
        "name": "The Musical Hop",
        "city": "San Francisco",
        "state": "CA",
        "num_upcoming_shows": 0,
    },
    {
        "name": "Park Square Live Music & Coffee",
        "city": "San Francisco",
        "state": "CA",
        "num_upcoming_shows": 1,
    },
    {
        "name": "The Dueling Pianos Bar",
        "city": "New York",
        "state": "NY",
        "num_upcoming_shows": 0,
    }
]

for venue in venues_data:
    cur.execute("""
        INSERT INTO Venue (name, city, state, num_upcoming_shows)
        VALUES (%s, %s, %s, %s)
    """, (venue["name"], venue["city"], venue["state"], venue["num_upcoming_shows"]))

# Create Artist table
cur.execute("""
    CREATE TABLE IF NOT EXISTS Artist (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL
    );
""")

# Insert data into Artist table
artists_data = [
    {"name": "Guns N Petals"},
    {"name": "Matt Quevedo"},
    {"name": "The Wild Sax Band"}
]

for artist in artists_data:
    cur.execute("""
        INSERT INTO Artist (name)
        VALUES (%s)
    """, (artist["name"],))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# App Config.
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Connect to a local PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:090194@127.0.0.1:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Models.
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

    # TODO: Implement any missing fields

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

    # TODO: Implement any missing fields

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
    # Query all distinct city and state combinations from the Venue table
    areas = db.session.query(Venue.city, Venue.state).distinct()

    # Initialize an empty list to store venue data
    data = []

    # Iterate over each city and state combination
    for area in areas:
        city, state = area

        # Query venues for the current city and state
        venues_in_area = Venue.query.filter_by(city=city, state=state).all()

        # Initialize an empty list to store venue data for the current city and state
        venue_data = []

        # Iterate over each venue in the current city and state
        for venue in venues_in_area:
            # Count the number of upcoming shows for the current venue (you need to implement this query)
            num_upcoming_shows = venue.shows.filter(Show.start_time > datetime.now()).count()

            # Append venue data to the list
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': num_upcoming_shows
            })

        # Append city, state, and venue data to the main data list
        data.append({
            'city': city,
            'state': state,
            'venues': venue_data
        })

    # Render the template with the fetched data
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Get the search term from the form data
    search_term = request.form.get('search_term', '')

    # Perform a case-insensitive partial string search for venues
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    # Initialize a list to store search results
    search_results = []

    # Iterate over the venues and construct the search results
    for venue in venues:
        # Count the number of upcoming shows for the current venue (you need to implement this query)
        num_upcoming_shows = venue.shows.filter(Show.start_time > datetime.now()).count()

        # Append venue data to the search results
        search_results.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_upcoming_shows
        })

    # Construct the response object
    response = {
        'count': len(search_results),
        'data': search_results
    }

    # Render the template with the search results and search term
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Query the venue with the given venue_id
    venue = Venue.query.get(venue_id)

    if not venue:
        # If the venue with the given venue_id does not exist, return a 404 error
        abort(404)

    # Query past shows for the venue
    past_shows = Show.query.join(Artist).filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all()

    # Query upcoming shows for the venue
    upcoming_shows = Show.query.join(Artist).filter(Show.venue_id == venue_id, Show.start_time >= datetime.now()).all()

    # Construct venue data
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(','),  # Assuming genres are stored as a comma-separated string in the database
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        } for show in past_shows],
        "upcoming_shows": [{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Extract form data
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    # Add other form fields as necessary

    try:
        # Create a new Venue object with the form data
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone)
        # Add the new Venue to the database
        db.session.add(new_venue)
        db.session.commit()
        # Flash success message
        flash('Venue ' + name + ' was successfully listed!')
    except:
        # If an error occurs during database insertion, rollback the session
        db.session.rollback()
        # Flash error message
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    finally:
        # Always close the database session
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # Query the venue to be deleted
        venue = Venue.query.get(venue_id)
        if not venue:
            # If the venue does not exist, return a 404 error
            abort(404)

        # Delete the venue from the database
        db.session.delete(venue)
        db.session.commit()
        # Flash success message
        flash('Venue was successfully deleted!')
    except Exception as e:
        # If an error occurs during deletion, rollback the session
        db.session.rollback()
        # Flash error message
        flash(f'An error occurred. Venue could not be deleted. Error: {str(e)}')
    finally:
        # Always close the database session
        db.session.close()

    # Redirect the user to the homepage
    return redirect(url_for('index'))  # Assuming 'index' is the name of the view function for the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Query all artists from the database
    artists = Artist.query.all()

    # Initialize an empty list to store artist data
    data = []

    # Iterate over each artist and construct the data
    for artist in artists:
        # Append artist data to the list
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    # Render the template with the fetched data
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Get the search term from the form data
    search_term = request.form.get('search_term', '')

    # Perform a case-insensitive partial string search for artists
    artists = Artist.query.filter(func.lower(Artist.name).contains(func.lower(search_term))).all()

    # Initialize a list to store search results
    search_results = []

    # Iterate over the artists and construct the search results
    for artist in artists:
        # Count the number of upcoming shows for the current artist (you need to implement this query)
        num_upcoming_shows = 0  # Placeholder, replace with actual query

        # Append artist data to the search results
        search_results.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': num_upcoming_shows
        })

    # Construct the response object
    response = {
        'count': len(search_results),
        'data': search_results
    }

    # Render the template with the search results and search term
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Query the artist with the given artist_id
    artist = Artist.query.get(artist_id)

    if not artist:
        # If the artist with the given artist_id does not exist, return a 404 error
        abort(404)

    # Query past shows for the artist
    past_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time < datetime.now()).all()

    # Query upcoming shows for the artist
    upcoming_shows = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time >= datetime.now()).all()

    # Construct artist data
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(','),  # Assuming genres are stored as a comma-separated string in the database
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Query the artist with the given artist_id
    artist = Artist.query.get(artist_id)

    if not artist:
        # If the artist with the given artist_id does not exist, return a 404 error
        abort(404)

    # Populate the ArtistForm with data from the queried artist
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Query the artist to be edited
    artist = Artist.query.get(artist_id)

    if not artist:
        # If the artist does not exist, return a 404 error
        abort(404)

    # Update the artist record with the form data
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    # Update other attributes as necessary

    try:
        # Commit the changes to the database
        db.session.commit()
        # Flash success message
        flash('Artist ' + artist.name + ' was successfully updated!')
    except:
        # If an error occurs during database update, rollback the session
        db.session.rollback()
        # Flash error message
        flash('An error occurred. Artist ' + artist.name + ' could not be updated.')
    finally:
        # Always close the database session
        db.session.close()

    # Redirect to the artist's page
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Query the venue with the given venue_id
    venue = Venue.query.get(venue_id)

    if not venue:
        # If the venue does not exist, return a 404 error
        abort(404)

    # Initialize the VenueForm and populate it with venue data
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Retrieve the venue from the database
    venue = Venue.query.get(venue_id)

    if not venue:
        # If the venue does not exist, return a 404 error
        abort(404)

    # Update the venue attributes with values from the form submitted
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    # Update other attributes as necessary

    try:
        # Commit the changes to the database
        db.session.commit()
        # Redirect to the show_venue page for the updated venue
        return redirect(url_for('show_venue', venue_id=venue_id))
    except Exception as e:
        # If an error occurs during database commit, rollback the session
        db.session.rollback()
        # Flash an error message
        flash('An error occurred. Venue could not be updated. Error: {}'.format(str(e)))
        # Redirect to the edit page for the venue
        return redirect(url_for('edit_venue', venue_id=venue_id))
    finally:
        # Always close the database session
        db.session.close()


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Extract form data
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    # Add other form fields as necessary

    try:
        # Create a new Artist object with the form data
        new_artist = Artist(name=name, city=city, state=state, phone=phone)
        # Add the new Artist to the database
        db.session.add(new_artist)
        db.session.commit()
        # Flash success message
        flash('Artist ' + name + ' was successfully listed!')
    except Exception as e:
        # If an error occurs during database insertion, rollback the session
        db.session.rollback()
        # Flash error message
        flash('An error occurred. Artist ' + name + ' could not be listed. Error: {}'.format(str(e)))
    finally:
        # Always close the database session
        db.session.close()

    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # Query shows data from the database
    shows = Show.query.all()

    # Initialize an empty list to store show data
    data = []

    # Iterate over each show and construct the show data
    for show in shows:
        # Construct show data
        show_data = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }
        # Append show data to the list
        data.append(show_data)

    # Render the template with the fetched show data
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Extract form data
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')

    try:
        # Create a new Show object with the form data
        new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)

        # Add the new Show to the database
        db.session.add(new_show)
        db.session.commit()

        # Flash success message
        flash('Show was successfully listed!')
    except Exception as e:
        # If an error occurs during database insertion, rollback the session
        db.session.rollback()
        
        # Flash error message
        flash('An error occurred. Show could not be listed.')

        # Log the error for debugging
        app.logger.error(str(e))
    finally:
        # Always close the database session
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

if __name__ == '__main__':
    # Run the Flask application on port 5000
    app.run(port=5000)
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
