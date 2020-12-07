import numpy as np
import datetime as dt
import collections

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"sean's sqlalchemy-challenge flask app<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Convert the query results to a dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date_query = session.query(func.max(Measurement.date)).first()
    last_date = last_date_query[0]
    (yr_str, mo_str, da_str) = last_date.split("-")
    yr = int(yr_str)
    mo = int(mo_str)
    da = int(da_str)
    last_date = dt.datetime(yr, mo, da)
    first_date = dt.datetime(yr, mo, da) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip_list = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date > first_date).\
                    filter(Measurement.date <= last_date).all()
    session.close()
    all_precip = []
    for date, precip in precip_list:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = precip
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_list = session.query(Measurement.station, Station.name, func.count(Measurement.station)).\
                        filter(Measurement.station == Station.station).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
    session.close()
    all_stations = []
    for station, name, count in station_list:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Count"] = count
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data
        Return a JSON list of temperature observations (TOBS) for the previous year.
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)
    station_list = session.query(Measurement.station, Station.name, func.count(Measurement.station)).\
                        filter(Measurement.station == Station.station).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
    most_active_station = station_list[0][0]
    last_date_query = session.query(func.max(Measurement.date)).first()
    last_date = last_date_query[0]
    (yr_str, mo_str, da_str) = last_date.split("-")
    yr = int(yr_str)
    mo = int(mo_str)
    da = int(da_str)
    last_date = dt.datetime(yr, mo, da)
    first_date = dt.datetime(yr, mo, da) - dt.timedelta(days=365)

    most_active_hist_list = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                                filter(Measurement.station == most_active_station).\
                                filter(Measurement.date > first_date).\
                                filter(Measurement.date <= last_date).all()
    session.close()

    all_tobs = []
    for station, date, tobs in most_active_hist_list:
        dict = {}
        dict["Station"] = station
        dict["Date"] = date
        dict["Temperature"] = tobs
        all_tobs.append(dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.        Return a JSON list of temperature observations (TOBS) for the previous year.
        When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    all_temps = []
    for tmin, tavg, tmax in results:
        dict = {}
        dict["Tmin"] = tmin
        dict["Tavg"] = tavg
        dict["Tmax"] = tmax
        all_temps.append(dict)

    return jsonify(all_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.        Return a JSON list of temperature observations (TOBS) for the previous year.
        When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.    """
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    session.close()
    all_temps = []
    for tmin, tavg, tmax in results:
        dict = {}
        dict["Tmin"] = tmin
        dict["Tavg"] = tavg
        dict["Tmax"] = tmax
        all_temps.append(dict)

    return jsonify(all_temps)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
