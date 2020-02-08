# Surfs Up
from flask import Flask, jsonify

# Add Dependencies
import numpy as np
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
def welcome():
    """List all available api routes."""
    return (
        f"<h2>Welcome to the Surfs Up! API</h2>"
        f"<h3>Available Routes:</h3>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Convert the query results to a Dictionary using date as the key and prcp as the value"""
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database
    max_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_2 = max_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_2, "%Y-%m-%d")

    # Subtract one year for start date.
    first_date = ((max_date - relativedelta(years = 1)).strftime('%Y-%m-%d'))

    # Perform a query to retrieve the date and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= first_date).order_by(Measurement.date.desc()).all()
    
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    precip_dict = {}
    for result in precip_data:
        precip_dict[result[0]] = result[1]


    return jsonify(precip_dict)

    session.close()

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    # List of the stations and the counts in descending order.
    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()

    return jsonify(stations)

    session.close()

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database
    max_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_2 = max_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_2, "%Y-%m-%d")

    # Subtract one year for start date.
    first_date = ((max_date - relativedelta(years = 1)).strftime('%Y-%m-%d'))

    # Query the last 12 months of temperature observation data for the past year.
    temp_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= first_date).all()

    return jsonify(temp_data)

    session.close()

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date until
    the end of the database."""
    session = Session(engine)

    #First we find the last date in the database
    max_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_2 = max_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_2, "%Y-%m-%d")

    # Pull min, avg, max temps utilizing the idea of the calc-temps function from the jupyter notebook
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= max_date).all()

    # Create list and dictionary to produce output.
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Min Temperature': temps[0][0]})
    return_list.append({'Avg Temperature': temps[0][1]})
    return_list.append({'Max Temperature': temps[0][2]})

    return jsonify(return_list)

    session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date until the end date."""
    session = Session(engine)

    # Pull min, avg, max temps utilizing the idea of the calc-temps function from the jupyter notebook
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create list and dictionary to produce output.
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Min Temperature': temps[0][0]})
    return_list.append({'Avg Temperature': temps[0][1]})
    return_list.append({'Max Temperature': temps[0][2]})

    return jsonify(return_list)

    session.close()

if __name__ == '__main__':
    app.run(debug=True)