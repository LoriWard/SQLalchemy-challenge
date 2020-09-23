#sqlalchemy-challenge 
#Climate App

#import dependencies

import pandas as pd
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


#setup database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


#reflect database

Base = automap_base()
Base.prepare(engine, reflect=True)


#save references to the table

measurement = Base.classes.measurement
station = Base.classes.station


#create session link 

session = Session(engine)

#Flask setup

app = Flask(__name__)



#Homepage - list all available API routes

@app.route("/")

def homepage():

    """List all available API routes"""

    return (
        f"Available API Routes for Hawaii Climate Info:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
            
           )


#Precipitation page
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")

def precipitation():

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).order_by(measurement.date).all()

    precipitation_list = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation_list.append(prcp_dict)

    session.close()

    return jsonify(precipitation_list)



#Weather stations
#Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")

def stations():

    session = Session(engine)

    stations = {}

    results = session.query(station.station, station.name).all()
    
    for sta, name in results:
        stations[sta] = name

    session.close()
 
    return jsonify(stations)


#Temperature Observations (TOBS) page
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")

def tobs():

   session = Session(engine)

   last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

   one_year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

   results = session.query(measurement.date, measurement.tobs).filter(measurement.date > one_year_ago).order_by(measurement.date).all()

   tobs_list = []

   for date, tobs in results:

        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    
   session.close()

   return jsonify(tobs_list)


#start and end dates
#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")

def start_date(start):

    session = Session(engine)

    start_date_list = []

    results =   session.query(  measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                        filter(measurement.date >= start).\
                        group_by(measurement.date).all()

    for date, min, avg, max in results:

        start_date_dict = {}
        start_date_dict["Date"] = date
        start_date_dict["TMIN"] = min
        start_date_dict["TAVG"] = avg
        start_date_dict["TMAX"] = max
        start_date_list.append(start_date_dict)

    session.close()    

    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start,end):

    
    session = Session(engine)

    start_date_list = []

    results =   session.query(  measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                        filter(and_(measurement.date >= start, measurement.date <= end)).\
                        group_by(measurement.date).all()

    for date, min, avg, max in results:
        start_date_dict = {}
        start_date_dict["Date"] = date
        start_date_dict["TMIN"] = min
        start_date_dict["TAVG"] = avg
        start_date_dict["TMAX"] = max
        start_date_list.append(start_date_dict)

    session.close()    

    return jsonify(start_date_list)


if __name__ == '__main__':
    app.run(debug=True)