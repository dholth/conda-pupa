from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path

app = FastAPI()

# Define a model for the package request
class PackageRequest(BaseModel):
    package_name: str
    version: Optional[str] = None

# Load your JSON data
default_file_name = "synthetic_repodata.json"
json_file_path = Path(__file__).parent / default_file_name
with open(json_file_path) as f:
    json_data = json.load(f)

@app.get("/synthetic_repodata")
async def get_json():
    return JSONResponse(content=json_data)

from .synth import handle_env_file
@app.get("/convert-to-synthetic")
async def convert_to_synthetic(file: UploadFile = File(...)):
    content = await file.read()
    synthetic_repodata = handle_env_file(content)
    return synthetic_repodata

@app.post("/package")
async def handle_package_request(request: PackageRequest):
    package_name = request.package_name
    version = request.version

    # Example logic for package handling
    if package_name in json_data:
        if version and version == json_data[package_name].get("version"):
            return JSONResponse(content=json_data[package_name])
        else:
            return JSONResponse(content={"message": "Version not found"}, status_code=404)
    else:
        return JSONResponse(content={"message": "Package not found"}, status_code=404)

@app.get("/redirect")
async def redirect_to_new_url():
    new_url = "https://example.com"  # Set your new URL here
    return RedirectResponse(url=new_url)