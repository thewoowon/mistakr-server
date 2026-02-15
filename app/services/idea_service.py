from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.idea import StartupIdea
from app.schemas.idea import IdeaCreate, IdeaUpdate


def create_idea(db: Session, user_id: int, idea: IdeaCreate) -> StartupIdea:
    db_idea = StartupIdea(user_id=user_id, **idea.model_dump())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


def get_ideas_by_user(db: Session, user_id: int) -> list[StartupIdea]:
    return db.query(StartupIdea).filter(StartupIdea.user_id == user_id).order_by(StartupIdea.created_at.desc()).all()


def get_idea_by_id(db: Session, idea_id: int, user_id: int) -> StartupIdea:
    idea = db.query(StartupIdea).filter(
        StartupIdea.id == idea_id,
        StartupIdea.user_id == user_id,
    ).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


def update_idea(db: Session, idea_id: int, user_id: int, update: IdeaUpdate) -> StartupIdea:
    idea = get_idea_by_id(db, idea_id, user_id)
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(idea, key, value)
    db.commit()
    db.refresh(idea)
    return idea


def delete_idea(db: Session, idea_id: int, user_id: int):
    idea = get_idea_by_id(db, idea_id, user_id)
    db.delete(idea)
    db.commit()
    return {"message": "Idea deleted successfully"}
