# PAMAS Run Guide

## Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

## Frontend
cd frontend
python3 -m http.server 5500

## URLs
Backend: http://localhost:8000
Docs: http://localhost:8000/docs
Frontend: http://localhost:5500/pamas-frontend.html

## PostgreSQL
brew services start postgresql
createdb pamas_db

## Blockchain
cd blockchain
npm install
npx hardhat compile
npx hardhat node
