import json
import secrets
from datetime import datetime

from database import Reading
from flask import Flask, jsonify, make_response, request
from flask_mongoengine import MongoEngine


def create_app(config_filename: str = "config.json") -> Flask:
    app = Flask(__name__)

    # TODO: randomize key gen
    app.config["SECRET_KEY"] = "secret!"

    app.config["MONGODB_SETTINGS"] = {
        "db": "mobius",
        "host": "localhost",
        "port": 27017,
    }

    app.config.from_file(config_filename, load=json.load)

    db = MongoEngine()
    db.init_app(app)

    @app.route("/<SENSOR_PATH>", methods=["POST"])
    def publish(SENSOR_PATH: str = ""):
        if SENSOR_PATH == "":
            return {}, 404

        reading: Reading = Reading.from_json(request.data.decode())
        reading.sensorPath = SENSOR_PATH
        reading.readingId = secrets.token_urlsafe(16)
        reading.save()

        return {}, 200

    @app.route("/<SENSOR_PATH>", methods=["GET"])
    # Impostare header
    def read(SENSOR_PATH: str = ""):
        if SENSOR_PATH == "":
            return {}, 404

        # Request args parsing
        sup_time_limit: str = request.args.get("crb", "")
        inf_time_limit: str = request.args.get("cra", "")
        n_limit: int = int(request.args.get("lim", "-1"))

        # Querying for SENSOR_PATH
        letture_raw = Reading.objects(sensorPath=SENSOR_PATH)  # type: ignore

        # Apply superior time limit if sup_time_limit length is valid
        if len(sup_time_limit) in [8, 15]:
            sup_time_limit = datetime.strptime(
                sup_time_limit,
                "%Y%m%d" if len(sup_time_limit) == 8 else "%Y%m%dT%H%M%S",
            ).isoformat()
            letture_raw = letture_raw.filter(readingTimestamp__lt=sup_time_limit)

        # Apply inferior time limit if inf_time_limit length is valid
        if len(inf_time_limit) in [8, 15]:
            inf_time_limit = datetime.strptime(
                inf_time_limit,
                "%Y%m%d" if len(inf_time_limit) == 8 else "%Y%m%dT%H%M%S",
            ).isoformat()
            letture_raw = letture_raw.filter(readingTimestamp__gt=inf_time_limit)

        # Apply quantity limit if n_limit is valid
        if n_limit != -1 and len(letture_raw) > n_limit:
            letture_raw = letture_raw[:n_limit]

        # Return if no reading is found
        if len(letture_raw) == 0:
            return {}, 404

        # Convert remaining readings to json
        letture: list[dict] = [x.to_json() for x in letture_raw]

        response = make_response(jsonify({"m2m:rsp": {"m2m:cin": letture}}))
        response.headers["X-M2M-Origin"] = ""
        response.headers["Content-Type"] = "application/vnd.onem2m-res+json;ty=4"
        response.headers["X-M2M-RI"] = datetime.isoformat(datetime.now())

        return response

    @app.route("/<SENSOR_PATH>/la", methods=["GET"])
    def read_last(SENSOR_PATH: str = ""):
        descending_time_readings = Reading.objects(
            sensorPath=SENSOR_PATH
        ).order_by(  # type: ignore
            "-readingTimestamp"
        )

        if len(descending_time_readings) == 0:
            return {}, 404

        response = make_response(
            jsonify({"m2m:cin": descending_time_readings[0].to_json()})
        )
        response.headers["X-M2M-Origin"] = ""
        response.headers["Content-Type"] = "application/vnd.onem2m-res+json;ty=4"
        response.headers["X-M2M-RI"] = datetime.isoformat(datetime.now())

        return response

    return app
