from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, db
from typing import Optional
import uuid
from datetime import datetime

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

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

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


if __name__== "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)