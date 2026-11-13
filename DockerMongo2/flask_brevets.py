
"""
Replacement for RUSA ACP brevet time calculator.
Includes MongoDB storage and retrieval for Project 5.
"""

import os
import logging

import arrow
import flask
from flask import request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

import acp_times
import config


# Application configuration
app = flask.Flask(__name__)
CONFIG = config.configuration(proxied=True)
app.secret_key = CONFIG.SECRET_KEY


# MongoDB connection
mongo_host = os.environ.get(
    "DB_PORT_27017_TCP_ADDR", "localhost"
)

client = MongoClient(
    mongo_host,
    27017,
    serverSelectionTimeoutMS=3000
)

db = client.brevets
controls_collection = db.controls


# Main calculator page
@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template("calc.html")


# Display saved controls
@app.route("/display")
def display():
    try:
        controls = list(
            controls_collection.find({}, {"_id": 0})
        )
    except PyMongoError:
        app.logger.exception("MongoDB query failed")
        return flask.jsonify(error="Database error"), 503

    return flask.render_template(
        "display.html",
        controls=controls
    )


# Save controls to MongoDB
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return flask.jsonify(
            error="Invalid JSON data"
        ), 400

    controls = data.get("controls")

    if not isinstance(controls, list) or not controls:
        return flask.jsonify(
            error="No controls to submit"
        ), 400

    valid_controls = []

    for control in controls:
        if not isinstance(control, dict):
            return flask.jsonify(
                error="Invalid control"
            ), 400

        km = control.get("km")
        open_time = control.get("open")
        close_time = control.get("close")

        if not km or not open_time or not close_time:
            return flask.jsonify(
                error="Incomplete control data"
            ), 400

        valid_controls.append({
            "miles": control.get("miles", ""),
            "km": km,
            "location": control.get("location", ""),
            "open": open_time,
            "close": close_time
        })

    try:
        result = controls_collection.insert_many(
            valid_controls
        )
    except PyMongoError:
        app.logger.exception("MongoDB insert failed")
        return flask.jsonify(
            error="Database error"
        ), 503

    return flask.jsonify(
        message="Controls saved successfully",
        count=len(result.inserted_ids)
    ), 201


# Calculate ACP opening and closing times
@app.route("/_calc_times")
def _calc_times():
    """
    Calculate control opening and closing times.

    Expected parameters:
        km: control distance in kilometers
        brevet_dist: total brevet distance
        start_time: ISO 8601 starting timestamp
    """

    app.logger.debug("Got a JSON request")

    km = request.args.get("km", type=float)
    brevet_dist = request.args.get(
        "brevet_dist", type=int
    )
    start_time = request.args.get(
        "start_time", type=str
    )

    app.logger.debug("km={}".format(km))
    app.logger.debug(
        "request.args: {}".format(request.args)
    )

    if (
        km is None
        or brevet_dist not in acp_times.BREVET_LIMITS
        or not start_time
    ):
        return flask.jsonify(
            error="Invalid or missing parameters"
        ), 400

    try:
        start = arrow.get(start_time)

        open_time = acp_times.open_time(
            km,
            brevet_dist,
            start.isoformat()
        )

        close_time = acp_times.close_time(
            km,
            brevet_dist,
            start.isoformat()
        )

    except (
        ValueError,
        TypeError,
        arrow.parser.ParserError
    ):
        return flask.jsonify(
            error="Invalid calculation parameters"
        ), 400

    return flask.jsonify(
        result={
            "open": open_time,
            "close": close_time
        }
    )


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")

    flask.session["linkback"] = flask.url_for(
        "index"
    )

    return flask.render_template(
        "404.html"
    ), 404


# Application startup
app.debug = getattr(CONFIG, "DEBUG", False)

if app.debug:
    app.logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    print(
        "Opening for global access on port {}".format(
            CONFIG.PORT
        )
    )

    app.run(
        port=CONFIG.PORT,
        host="0.0.0.0"
    )
