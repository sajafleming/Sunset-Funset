"""Sunset Project"""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
# from flask_sqlalchemy import SQLAlchemy

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

    # call into utilities functions to get list of lat and longs for best sunset spots

    
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

    app.run()