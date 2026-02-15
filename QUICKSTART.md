# 🚀 Quick Start Guide

## 📦 원클릭 설치 (권장)

```bash
cd /Users/aepeul/dev/server/MovieAndMe-server
./setup.sh
```

이 스크립트가 자동으로:
- ✅ Conda 환경 생성 (movieandme)
- ✅ Python 패키지 설치
- ✅ .env 파일 생성
- ✅ 데이터베이스 초기화

---

## ⚙️ 환경 설정

### 1. `.env` 파일 수정

```bash
nano .env
```

**필수 설정:**
```env
JWT_SECRET_KEY=your-super-secret-key-here-change-this
JWT_ALGORITHM=HS256

GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
```

> 💡 **Tip**: JWT_SECRET_KEY는 최소 32자 이상의 랜덤 문자열을 사용하세요.

---

## 🏃 서버 실행

```bash
./start.sh
```

서버가 실행되면:
- 🌐 API: http://localhost:8000
- 📚 Docs: http://localhost:8000/api/v1/docs
- 📖 ReDoc: http://localhost:8000/api/v1/redoc

---

## 🛠️ 수동 설치 (선택)

### 1. Conda 환경 생성
```bash
conda create -n movieandme python=3.11 -y
conda activate movieandme
```

### 2. 패키지 설치
```bash
pip install fastapi uvicorn pydantic-settings sqlalchemy python-decouple \
    alembic aiosqlite requests pyjwt python-multipart python-dotenv
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일 수정
```

### 4. 데이터베이스 초기화
```bash
./init_db.sh
# 또는
python -c "from app.db.session import sync_engine; from app.db.base import Base; from app.models import User, Token; Base.metadata.create_all(bind=sync_engine)"
```

### 5. 서버 실행
```bash
conda activate movieandme
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔍 테스트

### API 동작 확인
```bash
curl http://localhost:8000/api/v1/docs
```

### Google 로그인 테스트
1. React Native 앱에서 Google 로그인 시도
2. 서버 터미널에서 로그 확인
3. http://localhost:8000/api/v1/docs 에서 직접 테스트 가능

---

## 🐛 문제 해결

### ❌ 에러: "cannot import name 'Base'"
**해결:** 이미 수정됨! 최신 코드 사용

### ❌ 에러: "No module named 'fastapi'"
**해결:**
```bash
conda activate movieandme
pip install fastapi uvicorn
```

### ❌ 에러: "Database is locked"
**해결:**
```bash
rm app/db/movieandme.db
./init_db.sh
```

### ❌ CORS 에러
**해결:** [main.py:25-35](app/main.py#L25-L35)에서 `allow_origins`에 프론트엔드 URL 추가

---

## 📝 유용한 명령어

```bash
# DB 초기화
./init_db.sh

# 서버 시작
./start.sh

# Conda 환경 활성화
conda activate movieandme

# Conda 환경 비활성화
conda deactivate

# 패키지 목록 확인
pip list

# 서버 로그 실시간 확인
tail -f logs/server.log  # (로깅 설정 후)
```

---

## 🎯 다음 단계

1. ✅ 서버 실행 확인
2. 🔐 Google OAuth 설정
3. 📱 React Native 앱에서 테스트
4. 🎬 영화 API 기능 추가

더 자세한 내용은 [README.md](README.md) 참조!
