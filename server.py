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
import boto3
import botocore
import numpy as np
from io import BytesIO

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Raise error if trying to use undefined variable (otherwise it won't)
app.jinja_env.undefined = StrictUndefined

app.client = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
)

@app.route('/')
def home():
    """Homepage"""

    return render_template("homepage.html")

# @app.route('/intro')
# def intro():
#     """Intro page"""

#     return render_template("intro.html")

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

    # get value of the radio button for search radius
    radius = request.args.get("radio")
    print "RADIUS: {}".format(radius)

    latlong = (lat, lng)
    print "USER LATLONG: {}".format(latlong)

    n, w = get_filename_n_w(latlong)
    filename = create_filename(n, w)
    filepath = create_filepath(filename)
    print "FILENAME: {}".format(filename)
    print "FILEPATH: {}".format(filepath)

    # # for local
    # # validate that there is data for the location the user wants to search
    # if os.path.isfile(filepath):

    exists = True
        
    try:
        response = app.client.get_object(Bucket='sunsetfunset', Key=filename)
        # array = np.load(BytesIO(response['Body'].read()))host
        # print "ARRAY: {}".format(array)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False
            print "got here"
        else:
            print e
            raise e

    # if file in the bucket
    if exists:

        print "starting tile exists in bucket"
        # exact bounds of starting data tile
        exact_N_bound = n + .00166666666
        exact_W_bound = - (w + .0016666667)    

        # use SunsetViewFinder class to instantiate a new object
        # exact n and w bounds are now the bounds of the center tile
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

    else:
        return jsonify(error="Data not available")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = False

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    connect_to_db(app)

    app.run(host="0.0.0.0", port=8080)