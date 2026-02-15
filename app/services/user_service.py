from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import Token
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        profile_pic=user.profile_pic,
        provider=user.provider,
        provider_id=user.provider_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def check_email_exists(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None


def delete_user(db: Session, user_id: int):
    """
    Delete user and all related data (tokens, etc.)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete all user's tokens
    db.query(Token).filter(Token.user_id == user_id).delete()

    # Delete user
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
