from departure.router import router as departure_router
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

app.include_router(departure_router)
