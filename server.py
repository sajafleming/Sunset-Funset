"""Sunset Project"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from utilities import get_filename_n_w, create_filename, create_filepath
# from flask_debugtoolbar import DebugToolbarExtension
from find_sunset_spots import SunsetViewFinder
from flask_sqlalchemy import SQLAlchemy
from model import connect_to_db, db, LatLong
from get_photos import data_to_urls, request_flickr_data
import os

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raise error if trying to use undefined variable (otherwise it won't)
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def home():
    """Homepage"""

    # skeleton this

    return render_template("homepage.html")


@app.route('/intro')
def intro():
    """Intro page"""

    return render_template("intro.html")


@app.route('/data-not-available')
def notintro():
    """Look west and hope for the best :)"""

    return render_template("data-not-available.html")


@app.route('/sunset-spots', methods=["GET"])
def find_points():
    """Search results all pretty looking and such"""

    # get lat/lng from URL parameters named "lat" and "lng"
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))

    radius = request.args.get("radio")
    print "HELLO" * 5
    print radius

    latlong = (lat, lng)

    print "\n"
    print latlong


    n, w = get_filename_n_w(latlong)
    filename = create_filename(n, w)
    filepath = create_filepath(filename)

    # validate that there is data for the location the user wants to search
    if os.path.isfile(filepath):
        

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
        # sunset_spots = pick_n_best_points(latlong, exact_N_bound, exact_W_bound, radius)

        # use SunsetViewFinder class to instantiate a new object
        potential_sunset_spots = SunsetViewFinder(latlong, exact_N_bound, exact_W_bound, radius)
        sunset_spots = potential_sunset_spots.pick_best_points()

        # query all latlongs in flickr for pictures
        final_data = []
        latlong_pics_dict = {}

        for latlong in sunset_spots:

            data = request_flickr_data(latlong[0], latlong[1], .25)
            image_urls = data_to_urls(data)
            # for now just add the first url to the final urls list
            # maybe later I will have a better way of picking popular pictures

            # construct data dictionary
            final_data.append({"lat": latlong[0], "lng": latlong[1], "urls": image_urls})


        # final urls is now a dict containing latlongs and corresponding urls
        results = jsonify(sunset_spots=final_data)
        
        return results
        # return jsonify(hella)
        # google_json = request.form.get('user-location')
        # print google_json

    else:
        return jsonify(error="Data not available")
        #return redirect("/data-not-available")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    connect_to_db(app)

    app.run()