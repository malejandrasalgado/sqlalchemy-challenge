from flask import Flask, json, jsonify
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
def home():
      return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/" 
    )
#/api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    # Calculate the date one year from the last date in data set
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).\
        order_by(Measurement.date).all()
    session.close()
    
# Convert the query results to a dictionary using date as the key and prcp as the value
# Return the JSON representation of your dictionary

    # item_dict = {}
    # print(precipitation.__len__)
    
    # for item in precipitation:
    #     item_dict["date"] = item[0]
    #     item_dict["prcp"] = item[1]
    # print(item_dict)
    return jsonify(precipitation)

# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():

# Create our session (link) from Python to the DB
    session = Session(engine)
    station_list = session.query(Station.station).all()
    session.close()     
#Return a JSON list of stations from the dataset.
    return jsonify(station_list)


# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():

# Create our session (link) from Python to the DB
    session = Session(engine)

# Find the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    most_active_station_name = ""
    most_active_station = active_stations[0][0]
# Query the dates and temperature observations of the most active station for the last year of data.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    temperature_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).filter(Measurement.date >= last_year).\
    group_by(Measurement.date).all()
    session.close()
# Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(temperature_results)


# /api/v1.0/start_date
@app.route("/api/v1.0/<start_date>") 
def start_date(start_date):

# Create our session (link) from Python to the DB
    session = Session(engine)
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
# Query the minimum temperature, the average temperature, and the max temperature for a given start (for all dates greater than and equal to the start date)
    temperature_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    group_by(Measurement.date).all()
    session.close()
# Need to format the average number as this should be two decimal places only
    formatted_results =[]
    for result in temperature_results:
        new_result = [result[0],result[1],round(result[2],2),result[3]]
        formatted_results.append(new_result)
# Return a JSON list of temperature observations (TOBS) for the previous year.(for dates between the start and end date inclusive)
    return jsonify(formatted_results)


# /api/v1.0/<start_date>/<end_date>
@app.route("/api/v1.0/<start_date>/<end_date>")
def date_input(start_date, end_date):
# Create our session (link) from Python to the DB
    session = Session(engine)
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
# Query the minimum temperature, the average temperature, and the max temperature for a given start. 
    temperature_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    session.close()

# Need to format the average number as this should be two decimal places only
    formatted_results =[]
    for result in temperature_results:
        new_result = [result[0],result[1],round(result[2],2),result[3]]
        formatted_results.append(new_result)
# Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(formatted_results)


if __name__ == "__main__":
    app.run(debug=True)