from typing import Optional

from neighbor.service import NeighborService

from fastapi import FastAPI, File
from pydantic import BaseModel, Field

import logging

app = FastAPI()

service = NeighborService()
service.storage.connect()

@app.get("/nearest/{count}/{sourceType}/to/{postalCode}")
async def nearest(count, sourceType: str, postalCode: str):
    return service.getNearestNeighbor(count, sourceType, postalCode)
