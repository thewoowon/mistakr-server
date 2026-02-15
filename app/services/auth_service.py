from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.services.user_service import create_user
from app.core.security import decode_token
import requests
import jwt
from datetime import datetime, timedelta, timezone
from settings import (
    DEFAULT_PROFILE_PIC,
    GOOGLE_TOKEN_INFO_URL,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.models.user import User
from app.schemas.user import UserCreate
from app.models.token import Token
import os
import base64
import json
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
APPLE_PUBLIC_KEYS_URL = "https://appleid.apple.com/auth/keys"


def create_access_token(data: dict, expires_delta: timedelta):
    print("Creating access token with data:", data)
    to_encode = data.copy()
    print("Data to encode:", to_encode)
    expire = datetime.now(timezone.utc) + expires_delta
    print("Token expiration time:", expire)
    to_encode.update({"exp": expire})
    print("Final payload to encode:", to_encode)
    print("JWT Secret Key:", JWT_SECRET_KEY)
    print("JWT Algorithm:", JWT_ALGORITHM)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    print("Encoded JWT:", encoded_jwt)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def google_auth(request: Request, db: Session):
    try:
        
        data = await request.json()
        print("Received Google auth data:", data)
        
        email = data.get("email")
        print("Extracted email from request data:", email)

        if not email:
            raise HTTPException(status_code=400, detail="Email is missing in token")

        # 사용자 조회 또는 생성
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print("Creating new user for email:", email)
            # 새로운 사용자 생성
            user = create_user(
                db=db,
                user=UserCreate(
                    name=data.get("name", "Unknown"),
                    email=email,
                    profile_pic=data.get("photoUrl",DEFAULT_PROFILE_PIC),
                    provider="google",
                    provider_id=data.get("sub", ""),
                ),
            )
        print("User found/created:", user.email)

        # 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        print("Generating tokens for user:", user.email)

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        print("Access token generated for user:", user.email)
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires,
        )

        print("Generated tokens for user:", user.email)
        print("Access Token:", access_token)
        print("Refresh Token:", refresh_token)

        # Refresh Token을 DB에 저장
        existing_token = db.query(Token).filter(Token.user_id == user.id).first()
        if existing_token:
            existing_token.refresh_token = refresh_token
            existing_token.is_active = True
        else:
            new_token = Token(
                user_id=user.id, refresh_token=refresh_token, is_active=True
            )
            db.add(new_token)
        db.commit()

        print("Saved refresh token to database for user:", user.email)

        # 사용자 데이터 및 토큰 반환
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_pic": user.profile_pic,
            "provider": user.provider,
        }

        print("Returning user data and tokens")

        # RN 앱 형식에 맞게 헤더로 토큰 반환
        return JSONResponse(
            content={"user": user_data},
            status_code=200,
            headers={
                "Authorization": f"Bearer {access_token}",
                "RefreshToken": f"RefreshToken {refresh_token}",
            },
        )
    except Exception as e:
        print("Error:", e)
        print("Failed to verify token")
        raise HTTPException(status_code=400, detail="Invalid token")


def verify_apple_identity_token(identity_token: str):
    """
    Verify Apple's identity token and extract user information
    """
    try:
        # Decode the token header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(identity_token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg")

        if not kid or not alg:
            raise HTTPException(status_code=400, detail="Invalid token header")

        # Fetch Apple's public keys
        response = requests.get(APPLE_PUBLIC_KEYS_URL)
        apple_keys = response.json().get("keys", [])

        # Find the matching public key
        public_key = None
        for key in apple_keys:
            if key.get("kid") == kid:
                # Convert JWK to PEM format
                n = int.from_bytes(
                    base64.urlsafe_b64decode(key["n"] + "=="), byteorder="big"
                )
                e = int.from_bytes(
                    base64.urlsafe_b64decode(key["e"] + "=="), byteorder="big"
                )
                public_numbers = RSAPublicNumbers(e, n)
                public_key_obj = public_numbers.public_key(default_backend())
                public_key = public_key_obj.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
                break

        if not public_key:
            raise HTTPException(status_code=400, detail="Public key not found")

        # Verify and decode the token
        decoded_token = jwt.decode(
            identity_token,
            public_key,
            algorithms=[alg],
            audience=os.getenv("APPLE_BUNDLE_ID", "com.movieandme.app"),
        )

        print("Decoded Apple token:", decoded_token)
        return decoded_token

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Apple token has expired")
    except jwt.InvalidTokenError as e:
        print("Invalid Apple token:", e)
        raise HTTPException(status_code=400, detail="Invalid Apple token")
    except Exception as e:
        print("Error verifying Apple token:", e)
        raise HTTPException(status_code=400, detail="Failed to verify Apple token")


async def apple_auth(request: Request, db: Session):
    """
    Apple Sign In authentication
    """
    try:
        data = await request.json()
        print("Received Apple auth data:", data)

        identity_token = data.get("identityToken")
        email = data.get("email")
        name = data.get("name")

        if not identity_token:
            raise HTTPException(
                status_code=400, detail="Identity token is required"
            )

        # Verify Apple's identity token
        decoded_token = verify_apple_identity_token(identity_token)

        # Extract email from token (Apple provides email in the token)
        token_email = decoded_token.get("email")
        apple_user_id = decoded_token.get("sub")

        # Use email from request if available, otherwise use email from token
        user_email = email or token_email

        if not user_email:
            raise HTTPException(
                status_code=400, detail="Email not found in Apple token"
            )

        print("Apple user email:", user_email)
        print("Apple user ID:", apple_user_id)

        # Find or create user
        user = db.query(User).filter(User.email == user_email).first()

        if not user:
            print("Creating new user for Apple email:", user_email)
            # Create new user
            user = create_user(
                db=db,
                user=UserCreate(
                    name=name or "Apple User",
                    email=user_email,
                    profile_pic=DEFAULT_PROFILE_PIC,
                    provider="apple",
                    provider_id=apple_user_id,
                ),
            )
        else:
            print("Existing user found:", user.email)

        # Generate tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        print("Generating tokens for user:", user.email)

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires,
        )

        print("Generated tokens for Apple user:", user.email)

        # Save refresh token to database
        existing_token = db.query(Token).filter(Token.user_id == user.id).first()
        if existing_token:
            existing_token.refresh_token = refresh_token
            existing_token.is_active = True
        else:
            new_token = Token(
                user_id=user.id, refresh_token=refresh_token, is_active=True
            )
            db.add(new_token)
        db.commit()

        print("Saved refresh token to database for Apple user:", user.email)

        # Return user data and tokens
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_pic": user.profile_pic,
            "provider": user.provider,
        }

        print("Returning user data and tokens for Apple user")

        # Return tokens in headers (matching Google auth format)
        return JSONResponse(
            content={"user": user_data},
            status_code=200,
            headers={
                "Authorization": f"Bearer {access_token}",
                "RefreshToken": f"RefreshToken {refresh_token}",
            },
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print("Apple auth error:", e)
        raise HTTPException(status_code=400, detail="Apple authentication failed")


async def refresh_token_func(request: Request, db: Session):
    try:
        # Request Body에서 refreshToken 추출
        data = await request.json()
        refresh_token = data.get("refreshToken")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is required",
            )

        # Refresh Token 디코딩 및 검증
        try:
            payload = jwt.decode(
                refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("user_id")
        email = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # DB에서 refresh_token 조회
        token_obj = (
            db.query(Token)
            .filter(Token.user_id == user_id, Token.refresh_token == refresh_token)
            .first()
        )

        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if not token_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive refresh token",
            )

        # 새로운 Access Token & Refresh Token 발급
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        new_access_token = create_access_token(
            data={"sub": email, "user_id": user_id}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": email, "user_id": user_id},
            expires_delta=refresh_token_expires,
        )

        # DB의 refresh_token 업데이트
        token_obj.refresh_token = new_refresh_token
        db.commit()

        # RN 앱 형식에 맞게 헤더로 반환
        return JSONResponse(
            content={"message": "Token refreshed successfully"},
            status_code=200,
            headers={
                "Authorization": f"Bearer {new_access_token}",
                "RefreshToken": f"RefreshToken {new_refresh_token}",
            },
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
