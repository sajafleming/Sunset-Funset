"""Models and database functions for sunset project."""

from flask_sqlalchemy import SQLAlchemy
# from server import app

db = SQLAlchemy()


#######################################################################
#  Define data model

class LatLong(db.Model):
    """Latitude and longitude coordinates for each box"""

    __tablename__ = "latlongs"

    latlong_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    filename = db.Column(db.String(32), nullable=False)
    w_bound = db.Column(db.Float, nullable=False)
    e_bound = db.Column(db.Float, nullable=False)
    n_bound = db.Column(db.Float, nullable=False)
    s_bound = db.Column(db.Float, nullable=False)

    # numeric???????????


#######################################################################


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///coordinates'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."