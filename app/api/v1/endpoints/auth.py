from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.security import get_current_user
from app.services.auth_service import google_auth, apple_auth, refresh_token_func
from app.dependencies import get_db
from app.models.token import Token
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/google")
async def google(request: Request, db: Session = Depends(get_db)):
    """
    Google login for mobile app
    """
    return await google_auth(request, db)


@router.post("/apple")
async def apple(request: Request, db: Session = Depends(get_db)):
    """
    Apple Sign In for mobile app
    """
    return await apple_auth(request, db)


@router.post("/token/reissue")
async def token_reissue(request: Request, db: Session = Depends(get_db)):
    """
    RN app token refresh endpoint
    """
    return await refresh_token_func(request, db)


@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """
    Logout - invalidate refresh token
    """
    try:
        # Invalidate all user refresh tokens
        tokens = db.query(Token).filter(Token.user_id == user_id).all()
        for token in tokens:
            token.is_active = False
        db.commit()

        return JSONResponse(
            content={"message": "Logged out successfully"}, status_code=200
        )
    except Exception as e:
        print("Logout error:", e)
        raise HTTPException(status_code=400, detail="Logout failed")
