import sys
import transformers
from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from summarizer import generate_summary

app = FastAPI(title="Text Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://text-summarizer-mauve-six.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "python": sys.executable,
        "transformers_version": transformers.__version__,
        "transformers_path": transformers.__file__,
    }


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Please provide text to summarize.")

    if request.model not in {"textrank", "t5", "bart"}:
        raise HTTPException(
            status_code=400, detail="Model must be textrank, t5, or bart."
        )

    if request.summary_length not in {"short", "medium", "long"}:
        raise HTTPException(
            status_code=400, detail="Length must be short, medium, or long."
        )

    try:
        start = perf_counter()

        summary = generate_summary(
            text=text,
            model=request.model,
            summary_length=request.summary_length,
        )

        elapsed = perf_counter() - start

        return SummarizeResponse(
            summary=summary,
            model=request.model,
            original_words=len(text.split()),
            summary_words=len(summary.split()),
            processing_time_seconds=round(elapsed, 3),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(exc)}",
        ) from exc
