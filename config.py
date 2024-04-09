import os

# Generate a random secret key for Flask sessions
SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
import psycopg2

# Adjust the port number if necessary (use the default port 5432 for PostgreSQL)
conn = psycopg2.connect('host=127.0.0.1 dbname=fyyur user=postgres port=5432 password=090194')

# Create a cursor object to execute SQL queries
cur = conn.cursor()






# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:090194@127.0.0.1:5432/fyyur'