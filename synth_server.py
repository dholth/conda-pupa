import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI()


# Define a model for the package request
class PackageRequest(BaseModel):
    package_name: str
    version: Optional[str] = None


# Load your JSON data
with open("synthetic_repodata.json") as f:
    json_data = json.load(f)


@app.get("/synthetic_repodata")
async def get_json():
    return JSONResponse(content=json_data)


@app.post("/package")
async def handle_package_request(request: PackageRequest):
    package_name = request.package_name
    version = request.version

    # Example logic for package handling
    if package_name in json_data:
        if version and version == json_data[package_name].get("version"):
            return JSONResponse(content=json_data[package_name])
        else:
            return JSONResponse(
                content={"message": "Version not found"}, status_code=404
            )
    else:
        return JSONResponse(content={"message": "Package not found"}, status_code=404)


@app.get("/redirect")
async def redirect_to_new_url():
    new_url = "https://example.com"  # Set your new URL here
    return RedirectResponse(url=new_url)
