# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///C:/Users/dreww/Desktop/DataAnalysisWork/Assignments/sqlalchemy/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23').\
        order_by(measurement.date).all()
    
    session.close()

    prcp_last_year = {date: prcp for date, prcp in results}

    return jsonify(prcp_last_year)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(measurement.station, measurement.tobs).\
    filter(measurement.station == 'USC00519281',measurement.date >= '2016-08-23').\
        order_by(measurement.tobs).all()
        
    session.close()

    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    session = Session(engine)
    
    try:
        results = session.query(
            func.min(measurement.tobs).label('min_temp'),
            func.avg(measurement.tobs).label('avg_temp'),
            func.max(measurement.tobs).label('max_temp')
        ).filter(measurement.date >= start_date).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    session.close()

    if not results:
        return jsonify({"error": "No temperature data available for the specified date."}), 404

    min_temp, avg_temp, max_temp = results[0]

    temp_data = {
        'min_temp': min_temp,
        'avg_temp': avg_temp,
        'max_temp': max_temp
    }

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    session = Session(engine)

    try:
        results = session.query(
            func.min(measurement.tobs).label('min_temp'),
            func.avg(measurement.tobs).label('avg_temp'),
            func.max(measurement.tobs).label('max_temp')
        ).filter(measurement.date.between(start_date, end_date)).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    session.close()

    if not results:
        return jsonify({"error": "No temperature data available for the specified date range."}), 404

    min_temp, avg_temp, max_temp = results[0]

    temp_data = {
        'min_temp': min_temp,
        'avg_temp': avg_temp,
        'max_temp': max_temp
    }

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)