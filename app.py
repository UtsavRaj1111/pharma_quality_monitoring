import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import joblib
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "medicine.db")
MODEL_FILE = os.path.join(BASE_DIR, "models", "medicine_spoilage_model.joblib")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ------------------------
# Database model
# ------------------------
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    light = db.Column(db.Float, nullable=False)
    gas_level = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# create DB/tables if not present
with app.app_context():
    db.create_all()


# ------------------------
# Load ML model (if present)
# ------------------------
model = None
if os.path.exists(MODEL_FILE):
    try:
        model = joblib.load(MODEL_FILE)
        app.logger.info("Loaded ML model from %s", MODEL_FILE)
    except Exception as e:
        app.logger.warning("Failed to load model. Using fallback rule. Error: %s", e)
        model = None
else:
    app.logger.info("No ML model found at %s — using fallback rule.", MODEL_FILE)
    model = None


# ------------------------
# Prediction helper
# ------------------------
def predict_from_features(temp, hum, light, gas):
    try:
        t = float(temp)
        h = float(hum)
        l = float(light)
        g = float(gas)
    except Exception:
        return "OK"

    try:
        if model is not None:
            X = [[t, h, l, g]]
            pred = model.predict(X)[0]

            if isinstance(pred, (int, float)):
                return "Spoiled" if int(pred) == 1 else "OK"

            pstr = str(pred).lower()
            if pstr in ("spoiled", "1", "true", "yes"):
                return "Spoiled"
            if pstr in ("ok", "0", "false", "no"):
                return "OK"
            return "Spoiled" if "spo" in pstr else "OK"
        else:
            if t > 25 or h > 70 or g > 1000:
                return "Spoiled"
            return "OK"
    except Exception as exc:
        app.logger.error("Prediction error: %s", exc)
        return "OK"


# ------------------------
# Helper to build chart arrays safely
# ------------------------
def build_arrays_from_records(records):
    labels = [r.timestamp.strftime("%Y-%m-%d %H:%M:%S") for r in records]
    temps = [float(r.temperature) for r in records]
    hums = [float(r.humidity) for r in records]
    return labels, temps, hums


# ------------------------
# Routes
# ------------------------
@app.route("/", methods=["GET"])
def index():
    recs_desc = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
    records = list(reversed(recs_desc))
    labels, temps, hums = build_arrays_from_records(records) if records else ([], [], [])
    latest = recs_desc[0] if recs_desc else None

    return render_template(
        "index.html",
        latest=latest,
        records=recs_desc,
        labels=labels,
        temps=temps,
        hums=hums,
        prediction_result=None,
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        temp = request.form.get("temperature")
        hum = request.form.get("humidity")
        light = request.form.get("light")
        gas = request.form.get("gas_level")

        status = predict_from_features(temp, hum, light, gas)

        rec = SensorData(
            temperature=float(temp),
            humidity=float(hum),
            light=float(light),
            gas_level=float(gas),
            prediction=status,
        )
        db.session.add(rec)
        db.session.commit()

        recs_desc = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
        records = list(reversed(recs_desc))
        labels, temps, hums = build_arrays_from_records(records) if records else ([], [], [])
        latest = recs_desc[0] if recs_desc else None

        return render_template(
            "index.html",
            latest=latest,
            records=recs_desc,
            labels=labels,
            temps=temps,
            hums=hums,
            prediction_result=status,
        )
    except Exception as e:
        app.logger.error("Error in /predict: %s", e)
        return "Invalid input or server error", 400


@app.route("/data", methods=["GET"])
def data():
    recs_desc = SensorData.query.order_by(SensorData.timestamp.desc()).limit(10).all()
    records_json = [
        {
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": r.temperature,
            "humidity": r.humidity,
            "light": r.light,
            "gas_level": r.gas_level,
            "prediction": r.prediction,
        }
        for r in recs_desc
    ]

    records_chrono = list(reversed(recs_desc))
    labels, temps, hums = build_arrays_from_records(records_chrono) if records_chrono else ([], [], [])
    latest = recs_desc[0] if recs_desc else None
    latest_json = {
        "temperature": latest.temperature if latest else None,
        "humidity": latest.humidity if latest else None,
        "light": latest.light if latest else None,
        "gas_level": latest.gas_level if latest else None,
        "prediction": latest.prediction if latest else None,
    }

    return jsonify(
        {
            "records": records_json,
            "labels": labels,
            "temps": temps,
            "hums": hums,
            "latest": latest_json,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
