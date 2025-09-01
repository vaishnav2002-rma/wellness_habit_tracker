from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.database import users_collection, blacklist_collection
from bson import ObjectId
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Register
@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw
    }
    result = await users_collection.insert_one(new_user)
    return UserResponse(id=str(result.inserted_id), username=user.username, email=user.email)

# Login
@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_expires = timedelta(minutes=30)
    token = create_access_token(data={"sub": str(user["_id"])}, expires_delta=token_expires)

    return TokenResponse(access_token=token)

# Logout
@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Invalidate a token by storing it in blacklist"""
    await blacklist_collection.insert_one({"token": token})
    return {"msg": "Successfully logged out"}
