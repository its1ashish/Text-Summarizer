import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Optional

import transformers
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from summarizer import generate_summary

load_dotenv()
app = FastAPI(title="Text Summarizer API")
DB_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).with_name("summarizer.db")))
AUTH_SECRET = os.getenv("AUTH_SECRET", "development-only-change-me")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    with get_db() as db:
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS summaries (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), input_text TEXT NOT NULL, summary TEXT NOT NULL, model TEXT NOT NULL, summary_length TEXT NOT NULL, original_words INTEGER NOT NULL, summary_words INTEGER NOT NULL, processing_time_seconds REAL NOT NULL, created_at TEXT NOT NULL)")


initialize_db()
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", frontend_origin], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


def password_hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return f"{salt.hex()}${digest.hex()}"


def token_for(user_id):
    expiry = (datetime.now(timezone.utc) + timedelta(days=7)).timestamp()
    payload = base64.urlsafe_b64encode(json.dumps({"sub": user_id, "exp": expiry}).encode()).decode().rstrip("=")
    signature = hmac.new(AUTH_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload, signature = authorization[7:].split(".", 1)
        expected = hmac.new(AUTH_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = json.loads(decoded)
        if data["exp"] < datetime.now(timezone.utc).timestamp():
            return None
        with get_db() as db:
            user = db.execute("SELECT id, email FROM users WHERE id=?", (data["sub"],)).fetchone()
        return dict(user) if user else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def require_user(authorization):
    user = current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in to access your account.")
    return user


class AccountRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50000)
    model: str
    summary_length: str = "medium"


class SummarizeResponse(BaseModel):
    summary: str
    model: str
    original_words: int
    summary_words: int
    processing_time_seconds: float


class SaveSummaryRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=50000)
    summary: str = Field(min_length=1, max_length=50000)
    model: str
    summary_length: str
    original_words: int
    summary_words: int
    processing_time_seconds: float


@app.get("/api/health")
def health():
    return {"status": "ok", "python": sys.executable, "transformers_version": transformers.__version__, "transformers_path": transformers.__file__}


@app.post("/api/auth/register")
def register(request: AccountRequest):
    email = request.email.strip().lower()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    try:
        with get_db() as db:
            cursor = db.execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)", (email, password_hash(request.password), datetime.now(timezone.utc).isoformat()))
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    return {"token": token_for(user_id), "user": {"id": user_id, "email": email}}


@app.post("/api/auth/login")
def login(request: AccountRequest):
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (request.email.strip().lower(),)).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    salt, expected = user["password_hash"].split("$", 1)
    actual = password_hash(request.password, bytes.fromhex(salt)).split("$", 1)[1]
    if not hmac.compare_digest(actual, expected):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {"token": token_for(user["id"]), "user": {"id": user["id"], "email": user["email"]}}


@app.get("/api/auth/me")
def get_me(authorization: Optional[str] = Header(default=None)):
    return require_user(authorization)


@app.get("/api/history")
def history(authorization: Optional[str] = Header(default=None)):
    user = require_user(authorization)
    with get_db() as db:
        rows = db.execute("SELECT id,input_text,summary,model,summary_length,original_words,summary_words,processing_time_seconds,created_at FROM summaries WHERE user_id=? ORDER BY id DESC", (user["id"],)).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/history")
def save_history(request: SaveSummaryRequest, authorization: Optional[str] = Header(default=None)):
    user = require_user(authorization)
    if request.model not in {"textrank", "t5", "bart"} or request.summary_length not in {"short", "medium", "long"}:
        raise HTTPException(status_code=400, detail="Invalid model or summary length.")
    with get_db() as db:
        cursor = db.execute("INSERT INTO summaries(user_id,input_text,summary,model,summary_length,original_words,summary_words,processing_time_seconds,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (user["id"], request.input_text.strip(), request.summary, request.model, request.summary_length, request.original_words, request.summary_words, request.processing_time_seconds, datetime.now(timezone.utc).isoformat()))
    return {"id": cursor.lastrowid, "saved": True}


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, authorization: Optional[str] = Header(default=None)):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Please provide text to summarize.")
    if request.model not in {"textrank", "t5", "bart"}:
        raise HTTPException(status_code=400, detail="Model must be textrank, t5, or bart.")
    if request.summary_length not in {"short", "medium", "long"}:
        raise HTTPException(status_code=400, detail="Length must be short, medium, or long.")
    try:
        start = perf_counter()
        summary = generate_summary(text=text, model=request.model, summary_length=request.summary_length)
        elapsed = perf_counter() - start
        response = SummarizeResponse(summary=summary, model=request.model, original_words=len(text.split()), summary_words=len(summary.split()), processing_time_seconds=round(elapsed, 3))
        user = current_user(authorization)
        if user:
            with get_db() as db:
                db.execute("INSERT INTO summaries(user_id,input_text,summary,model,summary_length,original_words,summary_words,processing_time_seconds,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (user["id"], text, summary, request.model, request.summary_length, response.original_words, response.summary_words, response.processing_time_seconds, datetime.now(timezone.utc).isoformat()))
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(exc)}") from exc
