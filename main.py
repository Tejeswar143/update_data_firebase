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

@app.post("/sensor-data/")
def upload_sensor_data(data: SensorData):
    try:
        now = datetime.utcnow()

        payload = {
            "heartRate": data.heartRate,
            "spo2": data.spo2,
            "timestamp": now.isoformat()
        }
        
        ref = db.reference("/spo2_data").push()
        ref.set(payload)

        return {"message": "Data stored"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/temp-data/")
def upload_sensor_data(data: TempData):
    try:
        now = datetime.utcnow()

        payload = {
            "temp": data.temp,
            "timestamp": now.isoformat()
        }

        ref = db.reference("/temperature").push()
        ref.set(payload)

        return {"message": "Data stored"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ecg-data/")
def upload_sensor_data(data: EcgData):
    try:
        now = datetime.utcnow()
        payload = {
            "ecg": data.ecg,
            "timestamp": now.isoformat()
        }

        ref = db.reference("/ecg").push()
        ref.set(payload)

        return {"message": "Data stored"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__== "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)