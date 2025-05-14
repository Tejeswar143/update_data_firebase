from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
from typing import Optional
import uuid
from datetime import datetime
import os

# Firebase setup
cred = credentials.Certificate("./abcd.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://monitor-health-65515-default-rtdb.firebaseio.com/"
})

app = FastAPI()

class SensorData(BaseModel):
    heartRate: Optional[float]
    spo2: Optional[float]

class TempData(BaseModel):
    temp: Optional[float]

class EcgData(BaseModel):
    ecg: Optional[float]

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    with open("dashboard.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/latest-data")
def get_latest_data():
    try:
        now = datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)

        base_paths = {
            "temp": f"/temp_data/{year}/{month}/{day}",
            "spo2": f"/sensor_data/{year}/{month}/{day}",
            "ecg": f"/ecg_data/{year}/{month}/{day}"
        }

        def get_latest_value(path):
            ref = db.reference(path)
            data = ref.get()
            if not data:
                return None, None
            last_key = sorted(data.keys())[-1]
            return data[last_key], data[last_key]['timestamp']

        temp_data, temp_time = get_latest_value(base_paths["temp"])
        sensor_data, spo2_time = get_latest_value(base_paths["spo2"])
        ecg_data, ecg_time = get_latest_value(base_paths["ecg"])

        return {
            "temp": temp_data.get("temp") if temp_data else None,
            "tempTime": temp_time if temp_time else "No data",
            "spo2": sensor_data.get("spo2") if sensor_data else None,
            "spo2Time": spo2_time if spo2_time else "No data",
            "ecgTime": ecg_time if ecg_time else "No data"
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/sensor-data/")
def upload_sensor_data(data: SensorData):
    try:
        now = datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        unique_id = str(uuid.uuid4())

        path = f"/sensor_data/{year}/{month}/{day}/{unique_id}"

        payload = {
            "heartRate": data.heartRate,
            "spo2": data.spo2,
            "timestamp": now.isoformat()
        }

        db.reference(path).set(payload)

        return {"message": "Data stored", "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/temp-data/")
def upload_sensor_data(data: TempData):
    try:
        now = datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        unique_id = str(uuid.uuid4())

        path = f"/temp_data/{year}/{month}/{day}/{unique_id}"

        payload = {
            "temp": data.temp,
            "timestamp": now.isoformat()
        }

        db.reference(path).set(payload)

        return {"message": "Data stored", "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ecg-data/")
def upload_sensor_data(data: EcgData):
    try:
        now = datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)
        day = str(now.day).zfill(2)
        unique_id = str(uuid.uuid4())

        path = f"/ecg_data/{year}/{month}/{day}/{unique_id}"

        payload = {
            "temp": data.ecg,
            "timestamp": now.isoformat()
        }

        db.reference(path).set(payload)

        return {"message": "Data stored", "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__== "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)