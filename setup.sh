#!/bin/bash

# MovieAndMe Server Setup Script
echo "🎬 MovieAndMe Server Setup"
echo "=========================="

# 1. Conda 환경 확인 및 생성
if ! conda info --envs | grep -q "movieandme"; then
    echo "📦 Creating conda environment..."
    conda create -n movieandme python=3.11 -y
else
    echo "✅ Conda environment already exists"
fi

# 2. 환경 활성화
echo "🔄 Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate movieandme

# 3. 의존성 설치
echo "📥 Installing dependencies..."
pip install fastapi uvicorn pydantic-settings sqlalchemy python-decouple \
    alembic aiosqlite requests pyjwt python-multipart python-dotenv

# 4. .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials!"
else
    echo "✅ .env file exists"
fi

# 5. 데이터베이스 초기화
echo "🗄️  Initializing database..."
python -c "from app.db.session import sync_engine; from app.db.base import Base; from app.models import User, Token, Ticket, Movie, Diary; Base.metadata.create_all(bind=sync_engine)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Google OAuth credentials"
echo "2. Run: ./start.sh"
