from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserResponse, UserUpdate, ChangePasswordRequest
from app.utils.security import get_current_user, hash_password, verify_password
from app.database import users_collection, blacklist_collection
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])

# Get User Profile
@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"]
    )

# Update Profile (username, email, phone)
@router.put("/me", response_model=UserResponse)
async def update_user_profile(update_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # If email is being updated, check uniqueness
    if "email" in update_dict:
        existing = await users_collection.find_one({"email": update_dict["email"]})
        if existing and str(existing["_id"]) != str(current_user["_id"]):
            raise HTTPException(status_code=400, detail="Email already in use")

        # Invalidate tokens when email changes
        await blacklist_collection.insert_one({
            "user_id": str(current_user["_id"]),
            "reason": "email_changed"
        })

    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": update_dict},
        return_document=True
    )

    return UserResponse(
        id=str(result["_id"]),
        username=result["username"],
        email=result["email"]
    )

# Change Password
@router.put("/me/password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    # Verify old password
    if not verify_password(request.old_password, current_user["password"]):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    # Update password
    new_hashed_pw = hash_password(request.new_password)
    await users_collection.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"password": new_hashed_pw}}
    )

    # Invalidate all tokens for this user
    await blacklist_collection.insert_one({
        "user_id": str(current_user["_id"]),
        "reason": "password_changed"
    })

    return {"msg": "Password updated successfully. Please log in again."}
