from typing import Optional

from neighbor.service import NeighborService

from fastapi import FastAPI, File
from pydantic import BaseModel, Field

import logging
from decimal import Decimal
app = FastAPI()

service = NeighborService()
service.storage.connect()

@app.get("/nearest/{count}/{sourceType}/to/{postalCode}")
async def nearest(count: int, sourceType: str, postalCode: str):
    return service.getNearestNeighbor(count, sourceType, postalCode)

@app.get("/nearest/{count}/{sourceType}/to/{postalCode}/within/{miles}")
async def nearestWithin(count: int, sourceType: str, postalCode: str, miles:int):
    return service.getNearestNeighborWithin(count, sourceType, postalCode, miles)
