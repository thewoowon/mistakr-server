from fastapi import APIRouter
from app.api.v1.endpoints import user, auth, idea, consulting, case

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(idea.router, prefix="/ideas", tags=["ideas"])
api_router.include_router(consulting.router, prefix="/consulting", tags=["consulting"])
api_router.include_router(case.router, prefix="/cases", tags=["cases"])
