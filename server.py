"""Sunset Project"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from utilities import validate_location_for_search, find_local_maxima, pick_n_best_points
# from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from model import connect_to_db, db, LatLong

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raise error if trying to use undefined variable (otherwise it won't)
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """Homepage."""

    # skeleton this

    return render_template("homepage.html")

@app.route('/sunset-spots', methods=["GET"])
def search_results():
    """Search results all pretty looking and such"""

    # get lat/lng from URL parameters named "lat" and "lng"
    latlong = (36.79, -117.05) # placeholder

    # validate that the location the user wants to search is within the US
    if validate_location_for_search(latlong):
    # else return "I'm sorry, Sunset-Funset is not available in your area. Look west and hope for the best"

        # call into utilities functions to get list of lat and longs for best sunset spots
        points_of_elevation, radius_array = find_local_maxima(latlong)

        n_sunset_spots = pick_n_best_points(points_of_elevation, radius_array)

        # now convert idices to latlongs
        exact_coordinates = LatLong.query.filter_by(filename="n33w117")
        exact_N_bound = exact_coordinates[2] 

        print "HEY HERE I AM, I'M OVER HERE"
        print exact_N_bound
        
        # return JSON containing a list of lat/lng of best sunset spots

        hella = {"1": "you hella cool"}
        
        return jsonify(**hella)
        # google_json = request.form.get('user-location')
        # print google_json


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    connect_to_db(app)

    app.run()