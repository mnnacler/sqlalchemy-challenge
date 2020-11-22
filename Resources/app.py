import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Hawaii Homework available routes:</br>"
        f"</br>"
        f"Returns Precipitation Data for the last 12 months:</br>"
        f"/api/v1.0/precipitation</br>"
        f"</br>"
        f"Returns a list of all the stations:</br>"
        f"/api/v1.0/stations</br>"
        f"</br>"
        f"Returns tobs data for the last 12 months from the most active station:</br>"
        f"/api/v1.0/tobs</br>"
        f"</br>"
        f"Returns temperature data for the given start date and later:</br>"
        f"(Date must be in format 'yyyy-m-d')</br>"
        f"/api/v1.0/(start)</br>"
        f"</br>"
        f"Returns temperature data between 2 provided dates:</br>"
        f"(Dates must be in format 'yyyy-m-d')</br>"
        f"/api/v1.0/(start)/(end)</br>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #session = Session(engine)

    latestDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestDate = latestDate[0]
    prevYear = dt.datetime.strptime(latestDate, "%Y-%m-%d")- dt.timedelta(days=366)
    oneYear = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=prevYear).order_by(Measurement.date).all()

    precipitation = []
    for result in oneYear:
        precip_dict = {}
        precip_dict["date"] = result[0]
        precip_dict["prcp"] = result[1]
        precipitation.append(precip_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    stns = session.query(Station.name, Station.station).all()

    stations = []
    for result in stns:
        stn_dict = {}
        stn_dict["name"] = result[0]
        stn_dict["station"] = result[1]
        stations.append(stn_dict)
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp():
    latestDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestDate = latestDate[0]
    prevYear = dt.datetime.strptime(latestDate, "%Y-%m-%d")- dt.timedelta(days=366)
    activeStns = session.query(Measurement.station).group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()
    activeStns = activeStns[0]
    tempYear = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=prevYear).filter(Measurement.station == activeStns).\
        order_by(Measurement.date).all()
    
    tobs = []
    for result in tempYear:
        tobs_dict = {}
        tobs_dict["date"] = result[0]
        tobs_dict["tobs"] = result[1]
        tobs.append(tobs_dict)

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def startOnly(start):
    startDate = dt.datetime.strptime(start,"%Y-%m-%d")
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=startDate).all()
    TMIN = TMIN[0]
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=startDate).all()
    TAVG = TAVG[0]
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=startDate).all()
    TMAX = TMAX[0]
    return (
        f" The following statistics are for {startDate} and later:</br>"
        f"</br>"
        f" The minimum temperature is {TMIN} degrees.</br>"
        f" The average temperature is {TAVG} degrees.</br>"
        f" The average temperature is {TMAX} degrees.</br>"
        )

@app.route("/api/v1.0/<start>/<end>")
def startandEnd(start,end):
    startDate = dt.datetime.strptime(start,"%Y-%m-%d")
    endDate = dt.datetime.strptime(end,"%Y-%m-%d")
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=startDate).filter(Measurement.date<=endDate).all()
    TMIN = TMIN[0]
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=startDate).filter(Measurement.date<=endDate).all()
    TAVG = TAVG[0]
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=startDate).filter(Measurement.date<=endDate).all()
    TMAX = TMAX[0]
    return (
        f" The following statistics are for dates between {startDate} and {endDate}:</br>"
        f"</br>"
        f" The minimum temperature is {TMIN} degrees.</br>"
        f" The average temperature is {TAVG} degrees.</br>"
        f" The average temperature is {TMAX} degrees.</br>"
        )


if __name__ == "__main__":
    app.run(debug=True)
