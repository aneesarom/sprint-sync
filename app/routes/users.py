from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.services.supabase_client import supabase
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from datetime import datetime, timezone
from typing import List, Optional
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


class SignUpRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_admin: bool

class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    is_admin: bool


@router.post("/create")
def create_user(data: SignUpRequest):
    try:
        existing = supabase.table("users").select("*").eq("username", data.username).execute()
        if existing.data:
            logger.error(reason="Username already registered")
            raise HTTPException(status_code=409, detail="Username already registered")

        hashed_password = hash_password(data.password)

        res = supabase.table("users").insert({
            "email": data.email,
            "username": data.username,
            "password": hashed_password,
            "is_admin": data.is_admin
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Signup failed")

        user = res.data[0]
        access_token = create_access_token(user["id"])

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        res = supabase.table("users").select("*").eq("username", form_data.username).execute()

        if not res.data:
            logger.error(reason="User not found")
            raise HTTPException(status_code=404, detail="User not found")

        user = res.data[0]

        if not verify_password(form_data.password, user["password"]):
            logger.error(reason="Invalid password")
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = create_access_token(user["id"])

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{user_id}")
def update_user(user_id: str, data: UpdateUserRequest, current_user: dict = Depends(get_current_user)):
    try:
        if current_user["id"] != user_id and not current_user["is_admin"]:
            logger.error(reason="User doesn't have permission to update other users")
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can update other users.")

        update_data = {}

        if data.email:
            update_data["email"] = data.email

        if data.password:
            update_data["password"] = hash_password(data.password)

        if current_user["is_admin"]:
            update_data["is_admin"] = data.is_admin

        else:
            if data.is_admin:
                logger.error(reason="Only admins can grant admin privileges")
                raise HTTPException(status_code=403, detail="Only admins can grant admin privileges.")
            update_data["is_admin"] = data.is_admin

        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        res = supabase.table("users").update(update_data).eq("id", user_id).execute()

        if not res.data:
            logger.error(reason="Could not update user in database")
            raise HTTPException(status_code=500, detail="User Update failed")

        return {"message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            logger.error(reason="User doesn't have Admin privilege")
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can delete users.")
        
        if current_user["id"] == user_id:
            logger.error(reason="User attempted to delete their own account")
            raise HTTPException(status_code=400, detail="Cannot delete own account")

        res = supabase.table("users").delete().eq("id", user_id).execute()

        if not res.data:
            logger.error(reason="Could not delete user in database")
            raise HTTPException(status_code=500, detail="User Delete failed")

        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/list", response_model=List[UserResponse])
def list_users(current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            logger.error(reason="User doesn't have Admin privilege")
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can view all users.")
        
        res = supabase.table("users").select("*").execute()
        return res.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))