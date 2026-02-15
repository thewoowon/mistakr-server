from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.idea import IdeaCreate, IdeaUpdate, IdeaResponse
from app.services.idea_service import (
    create_idea, get_ideas_by_user, get_idea_by_id, update_idea, delete_idea,
)

router = APIRouter()


@router.post("", response_model=IdeaResponse)
def create(
    idea: IdeaCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """새 스타트업 아이디어 생성"""
    return create_idea(db, user_id, idea)


@router.get("")
def list_ideas(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 아이디어 목록"""
    ideas = get_ideas_by_user(db, user_id)
    return JSONResponse(content={"data": [IdeaResponse.model_validate(i).model_dump(mode="json") for i in ideas]})


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(
    idea_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """아이디어 상세 조회"""
    return get_idea_by_id(db, idea_id, user_id)


@router.put("/{idea_id}", response_model=IdeaResponse)
def update(
    idea_id: int,
    idea: IdeaUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """아이디어 수정"""
    return update_idea(db, idea_id, user_id, idea)


@router.delete("/{idea_id}")
def delete(
    idea_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """아이디어 삭제"""
    return delete_idea(db, idea_id, user_id)
