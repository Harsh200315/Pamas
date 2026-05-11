# PAMAS
### Provenance-Aware Media Authentication System

PAMAS is a research-oriented prototype for registering digital media, storing provenance metadata, and verifying uploaded content using cryptographic hashing, perceptual hashing, PostgreSQL, and blockchain-ready components.

---

## Overview

This project is designed to improve digital media authenticity verification by combining provenance-aware media registration with trust-based verification. It allows creators to register original content and later verify suspicious media using stored records, file fingerprints, and heuristic scoring.

---

## Tech Stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- FastAPI
- SQLAlchemy
- Python

**Database**
- PostgreSQL

**Blockchain**
- Solidity
- Hardhat

**Media Processing**
- SHA-256
- Pillow
- ImageHash

---

## Features

- Register media with creator details
- Generate SHA-256 fingerprint
- Compute perceptual hash for similarity analysis
- Store provenance records in PostgreSQL
- Verify uploaded media against stored records
- Return trust score and verdict:
  - `Authentic`
  - `Needs Review`
  - `Suspicious`
- Blockchain-ready smart contract prototype for media registry

---

## Project Structure

```bash
pamas-project/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   └── pamas-frontend.html
├── blockchain/
│   ├── contracts/
│   │   └── MediaRegistry.sol
│   ├── scripts/
│   │   └── deploy.js
│   ├── package.json
│   └── hardhat.config.js
└── docs/
    └── RUNNING.md
```

---

## Setup

### 1. PostgreSQL

```bash
brew install postgresql
brew services start postgresql
createdb pamas_db
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m py_compile app/main.py
uvicorn app.main:app --reload
```

Backend URLs:
- `http://localhost:8000`
- `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
python3 -m http.server 5500
```

Frontend URL:
- `http://localhost:5500/pamas-frontend.html`

### 4. Blockchain (Optional)

```bash
cd blockchain
npm install
npx hardhat compile
npx hardhat node
```

In another terminal:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Backend status |
| GET | `/health` | Health check |
| GET | `/records` | List all registered media |
| POST | `/register` | Register uploaded media |
| POST | `/verify` | Verify uploaded media |

---

## Workflow

### Register
- Upload media
- Enter creator information
- Generate SHA-256 and perceptual hash
- Store provenance metadata
- Return manifest, signature, and transaction ID

### Verify
- Upload media for analysis
- Compare against registered records
- Compute provenance score and heuristic risk score
- Return final verdict

---

## Current Scope

This implementation is a working **prototype** for provenance-aware media authentication.

It currently includes:
- media registration,
- provenance storage,
- hash-based verification,
- trust-score generation,
- blockchain-ready contract code.

It does **not yet include**:
- a trained FaceForensics++ model,
- deep learning based deepfake inference,
- live blockchain anchoring from backend,
- full IPFS production integration.

---

## Research Note

This repository matches a prototype implementation of a hybrid media authentication framework. If a paper claims full deepfake model training, benchmark evaluation, or FaceForensics++-based inference, those parts should be described as future work unless the corresponding model is implemented here.

---

## Troubleshooting

### Syntax check
```bash
python3 -m py_compile app/main.py
```

### Backend not starting
- Make sure PostgreSQL is running
- Make sure `pamas_db` exists
- Check `http://localhost:8000/docs`

### Registration or verification failing
- Start backend first
- Check backend terminal logs
- Confirm dependencies are installed

### Hardhat issue
```bash
nvm install 22
nvm use 22
```

---

## Future Work

- Integrate a trained deepfake detection model
- Add FaceForensics++ inference pipeline
- Connect backend to live blockchain transactions
- Add IPFS manifest storage
- Extend support to advanced video forensics

---

## License

This project is intended for academic and research demonstration purposes.