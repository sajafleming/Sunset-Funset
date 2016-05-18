"""Sunset Project"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from utilities import find_tile_name, create_filename, pick_n_best_points, validate_location_for_search
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
def find_points():
    """Search results all pretty looking and such"""

    # get lat/lng from URL parameters named "lat" and "lng"
    # latlong = (36.79, -117.05) # placeholder
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))

    latlong = (lat, lng)

    print "\n"
    print latlong

    # validate that the location the user wants to search is within the US
    if validate_location_for_search(latlong):

        
        filename_of_original_latlong, n, w = find_tile_name(latlong)
        print filename_of_original_latlong
        top_left_filename = create_filename(n + 1, w + 1) # want to add 1 to w here because filename represented as positive
        print "#############################################"
        print top_left_filename
        top_left_db_filename = top_left_filename.split(".")[0]
        print top_left_db_filename

        # TODO: add condition for if the top left tile doesn't exist
        # query db for exact coordinates of NW corner of master array
        exact_coordinates = LatLong.query.filter_by(filename=top_left_db_filename).first()
        exact_N_bound = exact_coordinates.n_bound
        exact_W_bound = exact_coordinates.w_bound

        # call into utilities functions to get list of lat and longs for best sunset spots

        n_sunset_spots = pick_n_best_points(latlong, exact_N_bound, exact_W_bound)
        
        # return JSON containing a list of lat/lng of best sunset spots

        # hella = {"1": "you hella cool"}
        # data = {"results": n_sunset_spots }
        results = jsonify({"results": n_sunset_spots})
        
        return results
        # return jsonify(hella)
        # google_json = request.form.get('user-location')
        # print google_json

    else:
        return jsonify(error="I'm sorry, Sunset-Funset is not available in your area. Look west and hope for the best :-)")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    connect_to_db(app)

    app.run()