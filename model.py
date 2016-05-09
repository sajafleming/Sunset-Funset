"""Models and database functions for sunset project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class LatLong(db.LatLong)
    """Latitude and longitude coordinates for each box"""

    __tablename__ = "latlongs"

    id = db.Column(db.Integer, autoincrement=False, primary_key=True)
    w_bound = db.Column(db., nullable=False)
    e_bound = db.Column(db.Float, nullable=False)
    n_bound = db.Column(db.Float, nullable=False)
    s_bound = db.Column(db.Float, nullable=False)


def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///coordinates'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."