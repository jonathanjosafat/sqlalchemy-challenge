# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import re

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def get_session():
    """Create a new session."""
    return Session(engine)

#################################################
# Flask Routes
#################################################
# Find the most recent date in the data set.


#1. '/'
#   - Start at the homepage.
#   - List all the available routes.

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

#2. /api/v1.0/precipitation
#   - Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary 
# using date as the key and prcp as the value.
#   - Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = get_session()
    try:
        one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= one_year).\
            order_by(Measurement.date.desc()).all()
        
        p_dict = {date: prcp for date, prcp in results}
        
        return jsonify(p_dict)
    finally:
        session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = get_session()
    try:
        sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
        queryresult = session.query(*sel).all()
        
        stations = []
        for station, name, lat, lon, el in queryresult:
            station_dict = {
                "Station": station,
                "Name": name,
                "Lat": lat,
                "Lon": lon,
                "Elevation": el
            }
            stations.append(station_dict)

        return jsonify(stations)
    finally:
        session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    session = get_session()
    try:
        one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
        queryresult = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= one_year).\
            all()
        
        tob_obs = [{"Date": date, "Tobs": tobs} for date, tobs in queryresult]
        
        return jsonify(tob_obs)
    finally:
        session.close()

@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    session = get_session()
    try:
        results = session.query(
            func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()
        
        temps = [{"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp} for min_temp, avg_temp, max_temp in results]
        
        return jsonify(temps)
    finally:
        session.close()

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = get_session()
    try:
        results = session.query(
            func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        
        temps = [{"Minimum Temperature": min_temp, "Average Temperature": avg_temp, "Maximum Temperature": max_temp} for min_temp, avg_temp, max_temp in results]
        
        return jsonify(temps)
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)