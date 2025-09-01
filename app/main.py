from fastapi import FastAPI
from app.routes import auth

app = FastAPI(title="Wellness & Habit Tracker")

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"msg": "Welcome to Wellness & Habit Tracker API"}
