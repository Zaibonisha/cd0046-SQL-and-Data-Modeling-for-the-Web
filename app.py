import psycopg2
from datetime import datetime

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


# Create Show table
cur.execute("""
    CREATE TABLE IF NOT EXISTS Show (
        id SERIAL PRIMARY KEY,
        venue_id INTEGER REFERENCES Venue(id),
        artist_id INTEGER REFERENCES Artist(id),
        start_time TIMESTAMP NOT NULL
    );
""")

# Insert data into Show table
shows_data = [
    {
        "venue_id": 1,
        "artist_id": 1,  # Assuming artist_id 1 corresponds to "Guns N Petals"
        "start_time": datetime.strptime("2019-05-21 21:30:00", "%Y-%m-%d %H:%M:%S")
    },
    {
        "venue_id": 3,
        "artist_id": 2,  # Assuming artist_id 2 corresponds to "Matt Quevedo"
        "start_time": datetime.strptime("2019-06-15 23:00:00", "%Y-%m-%d %H:%M:%S")
    },
    {
        "venue_id": 3,
        "artist_id": 3,  # Assuming artist_id 3 corresponds to "The Wild Sax Band"
        "start_time": datetime.strptime("2035-04-01 20:00:00", "%Y-%m-%d %H:%M:%S")
    },
    # Additional show data
]

for show in shows_data:
    cur.execute("""
        INSERT INTO Show (venue_id, artist_id, start_time)
        VALUES (%s, %s, %s)
    """, (show["venue_id"], show["artist_id"], show["start_time"]))    

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort,  jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
from flask_migrate import Migrate
import sys
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

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Models.
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Relationship with Artist model
    artists = db.relationship('Artist', backref='venue', lazy=True)

@app.route('/venues/create', methods=['POST'])
def create_venue():
    body = {}
    error = False
    try: 
        data = request.get_json()
        # Extract necessary fields from JSON
        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address')
        phone = data.get('phone')
        
        # Create a new Venue instance
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone)
        db.session.add(venue)
        db.session.commit()
        body['id'] = venue.id  # Return the ID of the newly created venue
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()           
        if error:
            abort(400)
        else:            
            return jsonify(body)

# Artist model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))

# Route for creating an artist
@app.route('/artists/create', methods=['POST'])
def create_artist():
    body = {}
    error = False
    try: 
        data = request.get_json()
        # Extract necessary fields from JSON
        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        phone = data.get('phone')
        genres = data.get('genres')
        image_link = data.get('image_link')
        facebook_link = data.get('facebook_link')
        venue_id = data.get('venue_id')
        
        # Create a new Artist instance
        artist = Artist(name=name, city=city, state=state, phone=phone, 
                        genres=genres, image_link=image_link, 
                        facebook_link=facebook_link, venue_id=venue_id)
        db.session.add(artist)
        db.session.commit()
        body['id'] = artist.id  # Return the ID of the newly created artist
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()           
        if error:
            abort(400)
        else:            
            return jsonify(body)

# Show model
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))

@app.route('/shows/create', methods=['POST'])
def create_show():
    body = {}
    error = False
    try:
        data = request.get_json()
        venue_id = data.get('venue_id')
        artist_id = data.get('artist_id')
        start_time = data.get('start_time')

        show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        body['id'] = show.id
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(body)

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
    # Replace with real venues data
    # Query venues from the database
    venues = Venue.query.all()
    data = []
    for venue in venues:
        venue_data = {
            "city": venue.city,
            "state": venue.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": 0,  # You need to calculate this based on actual data
            }]
        }
        data.append(venue_data)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    # Implement search logic here
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0,  # You need to calculate this based on actual data
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    # Perform necessary data processing
    # Example data
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [],  # You need to fetch genres from venue object
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": "",  # You need to fetch website from venue object
        "facebook_link": "",  # You need to fetch facebook_link from venue object
        "seeking_talent": False,  # You need to fetch seeking_talent from venue object
        "seeking_description": "",  # You need to fetch seeking_description from venue object
        "image_link": "",  # You need to fetch image_link from venue object
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0
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
    artists = Artist.query.all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(artists),
        "data": [{"id": artist.id, "name": artist.name, "num_upcoming_shows": 0} for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [],  # You need to fetch genres from artist object
        "city": "",  # You need to fetch city from artist object
        "state": "",  # You need to fetch state from artist object
        "phone": "",  # You need to fetch phone from artist object
        "website": "",  # You need to fetch website from artist object
        "facebook_link": "",  # You need to fetch facebook_link from artist object
        "seeking_venue": False,  # You need to fetch seeking_venue from artist object
        "seeking_description": "",  # You need to fetch seeking_description from artist object
        "image_link": "",  # You need to fetch image_link from artist object
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0
    }
    return render_template('pages/show_artist.html', artist=data)


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
    # Fetch shows data from the database and pass it to the template
    shows = Show.query.all()
    return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    if form.validate():
        description = form.description.data
        # Create a new show record in the database
        show = Show(description=description)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    else:
        flash('An error occurred. Show could not be listed.')
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