from fastapi import FastAPI
from app.routes import auth, users, habits

app = FastAPI(title="Wellness & Habit Tracker")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(habits.router)

@app.get("/")
async def root():
    return {"msg": "Welcome to Wellness & Habit Tracker API"}
