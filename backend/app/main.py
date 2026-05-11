from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from hashlib import sha256
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
import imagehash
import json
import base64
import time
import uuid
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://localhost/pamas_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class MediaRecord(Base):
    __tablename__ = "media_records"

    id = Column(Integer, primary_key=True, index=True)
    creator_name = Column(String, index=True)
    creator_id = Column(String, index=True)
    file_name = Column(String)
    media_type = Column(String)
    sha256_hash = Column(String, unique=True, index=True)
    perceptual_hash = Column(String, index=True)
    description = Column(Text)
    manifest_json = Column(Text)
    signature = Column(Text)
    tx_id = Column(String)
    created_at = Column(String)


app = FastAPI(title="PAMAS API", version="2.3.0")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def file_sha256(file_bytes):
    return sha256(file_bytes).hexdigest()


def compute_perceptual_hash(file_bytes, media_type):
    try:
        if media_type.startswith("image/"):
            image_obj = Image.open(BytesIO(file_bytes)).convert("RGB")
            return str(imagehash.phash(image_obj))
        return "video-" + str(len(file_bytes) // 1024)
    except Exception:
        return "unknown"


def hamming_hex(value_a, value_b):
    if len(value_a) != len(value_b):
        return 999
    try:
        return bin(int(value_a, 16) ^ int(value_b, 16)).count("1")
    except Exception:
        return 999


def sign_manifest(manifest):
    payload = json.dumps(manifest, sort_keys=True).encode()
    digest = sha256(payload).digest()
    return base64.b64encode(digest).decode()


def fake_tx_id(seed):
    raw_value = seed + str(time.time()) + str(uuid.uuid4())
    return "0x" + sha256(raw_value.encode()).hexdigest()[:32]


def deepfake_risk_estimate(media_type, file_size, provenance_strength):
    risk = 0.25

    if media_type.startswith("video/"):
        risk = risk + 0.15

    if file_size < 100000:
        risk = risk + 0.10

    if provenance_strength == "exact":
        risk = risk - 0.18
    elif provenance_strength == "similar":
        risk = risk - 0.06
    else:
        risk = risk + 0.12

    risk = round(risk, 3)

    if risk < 0.03:
        risk = 0.03

    if risk > 0.96:
        risk = 0.96

    return risk


@app.get("/")
def root():
    return {"message": "PAMAS backend running with PostgreSQL"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/records")
def list_records():
    db = SessionLocal()
    try:
        rows = db.query(MediaRecord).order_by(MediaRecord.id.desc()).all()
        result_rows = []

        for row in rows:
            row_data = {
                "id": row.id,
                "creator_name": row.creator_name,
                "creator_id": row.creator_id,
                "file_name": row.file_name,
                "media_type": row.media_type,
                "sha256": row.sha256_hash,
                "perceptual_hash": row.perceptual_hash,
                "tx_id": row.tx_id,
                "created_at": row.created_at,
            }
            result_rows.append(row_data)

        return result_rows
    finally:
        db.close()


@app.post("/register")
async def register_media(
    creator_name: str = Form(...),
    creator_id: str = Form(...),
    description: str = Form(""),
    media: UploadFile = File(...),
):
    try:
        file_bytes = await media.read()

        if file_bytes is None:
            return JSONResponse(
                status_code=400,
                content={"error": "No file data received"}
            )

        if len(file_bytes) == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty file uploaded"}
            )

        media_type = media.content_type or "application/octet-stream"
        sha_hash = file_sha256(file_bytes)
        perceptual_hash_value = compute_perceptual_hash(file_bytes, media_type)
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        manifest = {
            "creator_name": creator_name,
            "creator_id": creator_id,
            "file_name": media.filename,
            "media_type": media_type,
            "sha256": sha_hash,
            "perceptual_hash": perceptual_hash_value,
            "description": description,
            "created_at": created_at,
        }

        signature = sign_manifest(manifest)
        tx_id = fake_tx_id(sha_hash)

        db = SessionLocal()
        try:
            existing_record = db.query(MediaRecord).filter_by(sha256_hash=sha_hash).first()

            if existing_record is not None:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Media already registered",
                        "tx_id": existing_record.tx_id
                    }
                )

            new_record = MediaRecord(
                creator_name=creator_name,
                creator_id=creator_id,
                file_name=media.filename,
                media_type=media_type,
                sha256_hash=sha_hash,
                perceptual_hash=perceptual_hash_value,
                description=description,
                manifest_json=json.dumps(manifest),
                signature=signature,
                tx_id=tx_id,
                created_at=created_at,
            )

            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            response_payload = {
                "message": "Media registered successfully",
                "manifest": manifest,
                "signature": signature,
                "tx_id": tx_id,
            }

            return response_payload
        finally:
            db.close()

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )


@app.post("/verify")
async def verify_media(
    claimed_creator: str = Form(""),
    media: UploadFile = File(...),
):
    try:
        file_bytes = await media.read()

        if file_bytes is None:
            return JSONResponse(
                status_code=400,
                content={"error": "No file data received"}
            )

        if len(file_bytes) == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty file uploaded"}
            )

        media_type = media.content_type or "application/octet-stream"
        sha_hash = file_sha256(file_bytes)
        perceptual_hash_value = compute_perceptual_hash(file_bytes, media_type)

        db = SessionLocal()
        try:
            exact_match = db.query(MediaRecord).filter_by(sha256_hash=sha_hash).first()
            all_records = db.query(MediaRecord).all()

            nearest_match = None
            nearest_distance = 999

            for row in all_records:
                current_distance = hamming_hex(row.perceptual_hash, perceptual_hash_value)
                if current_distance < nearest_distance:
                    nearest_distance = current_distance
                    nearest_match = row

            provenance_score = 0.0
            provenance_status = "No matching record found"
            provenance_strength = "none"
            matched_record = None

            if exact_match is not None:
                matched_record = exact_match
                provenance_score = 1.0
                provenance_status = "Exact provenance match found for " + exact_match.creator_name
                provenance_strength = "exact"
            else:
                use_nearest = False

                if nearest_match is not None:
                    if nearest_distance <= 10:
                        if nearest_match.perceptual_hash != "unknown":
                            if perceptual_hash_value != "unknown":
                                use_nearest = True

                if use_nearest is True:
                    matched_record = nearest_match
                    provenance_score = 0.55
                    provenance_status = (
                        "Approximate match found for "
                        + nearest_match.creator_name
                        + " (distance "
                        + str(nearest_distance)
                        + ")"
                    )
                    provenance_strength = "similar"

            if claimed_creator != "":
                if matched_record is not None:
                    if matched_record.creator_name.lower() == claimed_creator.lower():
                        provenance_score = provenance_score + 0.05
                        if provenance_score > 1.0:
                            provenance_score = 1.0
                    else:
                        provenance_score = provenance_score - 0.08
                        if provenance_score < 0.0:
                            provenance_score = 0.0

            risk = deepfake_risk_estimate(media_type, len(file_bytes), provenance_strength)
            trust_score = 0.62 * provenance_score + 0.38 * (1 - risk)
            trust_score = round(trust_score, 3)

            if trust_score < 0.0:
                trust_score = 0.0

            if trust_score > 1.0:
                trust_score = 1.0

            if trust_score >= 0.8:
                verdict = "Authentic"
            elif trust_score >= 0.5:
                verdict = "Needs Review"
            else:
                verdict = "Suspicious"

            matched_payload = None

            if matched_record is not None:
                matched_payload = {
                    "creator_name": matched_record.creator_name,
                    "creator_id": matched_record.creator_id,
                    "file_name": matched_record.file_name,
                    "tx_id": matched_record.tx_id,
                    "created_at": matched_record.created_at,
                }

            response_payload = {
                "sha256": sha_hash,
                "perceptual_hash": perceptual_hash_value,
                "provenance_score": provenance_score,
                "provenance_status": provenance_status,
                "deepfake_risk": risk,
                "trust_score": trust_score,
                "verdict": verdict,
                "matched_record": matched_payload
            }

            return response_payload
        finally:
            db.close()

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )
