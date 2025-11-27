# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserSchema, UserCreate
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash
from app.api.dependencies import make_container_dep
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=UserSchema)
async def create_user(
    user_in: UserCreate,
    users_container = Depends(make_container_dep("users")),
):
    """
    Create a new user
    """
    try:
        user_repo = UserRepository(container=users_container)
        user = user_repo.get_user_by_email(email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        
        hashed_password = get_password_hash(user_in.password)
        user = user_repo.create_user(
            user_in.copy(update={"hashed_password": hashed_password})
        )
        return UserSchema.model_validate(user)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: str,
    users_container = Depends(make_container_dep("users")),
):
    """
    Get a specific user by id.
    """
    user_repo = UserRepository(container=users_container)
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return UserSchema.model_validate(user)
