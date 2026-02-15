from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.schemas.user import EmailVerificationResponse, UserResponse
from app.services.user_service import (
    check_email_exists,
    get_user_by_email,
    get_user_by_id,
    delete_user,
)
from app.dependencies import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/me")
def read(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user from access token
    """
    user = get_user_by_id(db=db, user_id=user_id)

    return JSONResponse(
        content={
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile_pic": user.profile_pic,
                "provider": user.provider,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        },
        status_code=200,
    )


@router.get("/email/{email}", response_model=UserResponse)
def read_by_email(email: EmailStr, db: Session = Depends(get_db)):
    """
    Get user by email
    """
    return get_user_by_email(db=db, email=email)


@router.get("/verify", response_model=EmailVerificationResponse)
def verify_email(email: EmailStr, db: Session = Depends(get_db)):
    """
    Check if an email is already registered
    """
    return {"exists": check_email_exists(db=db, email=email)}


@router.delete("/me")
def delete_current_user(
    user_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Delete current user account
    """
    result = delete_user(db=db, user_id=user_id)
    return JSONResponse(content=result, status_code=200)
