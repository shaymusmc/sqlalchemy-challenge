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

#create session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
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

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset."""
    # List of the stations and the counts in descending order.
    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

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

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date until
    the end of the database."""
    ## USING calc_temps AND SOME IDEATION OF RETURN LIST INSPIRED BY GITHUB USER ejhagee, THEN MODIFIED FOR MY CODE AND STYLE

    #First we find the last date in the database
    max_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_2 = max_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_2, "%Y-%m-%d")

    # Pull min, avg, max temps utilizing the calc-temps function from the jupyter notebook
    temps = calc_temps(start, max_date)

    # Create list and dictionary to produce output.
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Min Temperature': temps[0][0]})
    return_list.append({'Avg Temperature': temps[0][1]})
    return_list.append({'Max Temperature': temps[0][2]})

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date unitl
    the end date."""
    ## USING calc_temps AND SOME IDEATION OF RETURN LIST INSPIRED BY GITHUB USER ejhagee, THEN MODIFIED FOR MY CODE AND STYLE

    # Pull min, avg, max temps utilizing the calc-temps function from the jupyter notebook
    temps = calc_temps(start, end)

    # Create list and dictionary to produce output.
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Min Temperature': temps[0][0]})
    return_list.append({'Avg Temperature': temps[0][1]})
    return_list.append({'Max Temperature': temps[0][2]})

    return jsonify(return_list)


if __name__ == '__main__':
    app.run(debug=True)