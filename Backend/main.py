from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/style", StaticFiles(directory="style"), name="style")

class COVIDData(BaseModel):
    dateRep: str
    day: str
    month: str
    year: str
    cases: int
    deaths: int
    countriesAndTerritories: str
    geoId: str
    countryterritoryCode: str
    popData2019: Optional[float]
    continentExp: str
    cumulative_number_for_14_days_of_COVID_19_cases_per_100000: Optional[str]

    @validator('dateRep', 'countriesAndTerritories', 'geoId', 'continentExp')
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Must not be empty')
        return v

processed_data = []

@app.post("/api/data")
async def receive_data(data: List[COVIDData]):
    valid_data = [d.dict() for d in data]
    processed_data.extend(valid_data)
    with open("style/processed_data.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    return JSONResponse(content={"status": "success", "processed_data": valid_data})

@app.get("/api/data")
async def get_data():
    try:
        with open("style/processed_data.json", "r") as f:
            stored_data = json.load(f)
        return JSONResponse(content={"status": "success", "data": stored_data})
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Data not found"})

@app.get("/")
async def main():
    return FileResponse("style/index.html")

@app.get("/filtered_european_data.json")
async def get_filtered_european_data():
    return FileResponse("style/filtered_european_data.json")

@app.get("/script.js")
async def get_script_js():
    return FileResponse("style/script.js")

@app.get("/style/{filename:path}")
async def get_static(filename: str):
    return FileResponse(os.path.join("style", filename))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)