import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect,func

from flask import Flask, jsonify

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#View the classes automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)
session = Session(engine)
#Flask Routes

@app.route("/")
def home():
    return(
        f"Available routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Enter sdate and edate in yyyy-mm-dd format <br/>"
        f"/api/v1.0/start/<sdate> <br/>"
        f"/api/v1.0/startend/<sdate>/<edate> <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>="2016-08-23").all()
    results_array = list(np.ravel(results))
    
    results_dict= []
    for date,prcp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["prcp"] = prcp
        results_dict.append(temp_dict)
    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    results = (session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date>="2016-08-23").\
            filter(Measurement.date<="2017-08-23").\
            filter(Measurement.station == "USC00519281")).all()
    tobs_active_station = list(np.ravel(results))
    return jsonify(tobs_active_station)

@app.route("/api/v1.0/start/<sdate>")
def start(sdate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= sdate)
                       .group_by(Measurement.date)
                       .all())
    calc_temps = list(np.ravel(results))
    return jsonify(calc_temps)

@app.route("/api/v1.0/startend/<sdate>/<edate>")
def startend(sdate,edate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= sdate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= edate)
                       .group_by(Measurement.date)
                       .all())
    calc_temps = list(np.ravel(results))
    return jsonify(calc_temps)

if __name__ == '__main__':
    app.run(debug=True)