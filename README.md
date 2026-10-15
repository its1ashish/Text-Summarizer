# Text Summarizer

A text summarization web application that generates concise summaries using extractive and abstractive NLP techniques. The application provides three summarization options: TextRank, T5-small, and BART.

## Features

- **TextRank:** Extractive summarization that selects important sentences from the original text.
- **T5-small:** Abstractive summarization using a pretrained transformer model.
- **BART:** Abstractive summarization using the pretrained `facebook/bart-large-cnn` model.
- **Summary length selection:** Choose short, medium, or long summaries.
- **Model comparison:** Generate summaries using all three models and compare their results.
- **Summary statistics:** View original and summarized word counts and processing time.
- **Copy summary:** Copy generated summaries to the clipboard.
- **REST API:** Generate summaries through a FastAPI backend.

## Tech Stack

**Frontend**
- React
- Vite
- JavaScript
- CSS

**Backend**
- Python
- FastAPI
- Uvicorn
- Hugging Face Transformers
- PyTorch
- Sumy
- NLTK

## Project Structure

```text
Text-Summarizer/
├── backend/
│   ├── tests/
│   │   └── test_main.py
│   ├── main.py
│   ├── summarizer.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── Text_Summarization.ipynb
├── LICENSE
└── README.md
```

## Prerequisites

- Python 3.10 or a compatible Python version
- Node.js and npm
- Sufficient memory and disk space for the transformer models

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/its1ashish/Text-Summarizer.git
cd Text-Summarizer
```

### 2. Set up the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start the backend

From the `backend/` directory, run:

```bash
python -m uvicorn main:app --reload --port 8000
```

The API will be available at:

- API base URL: `http://127.0.0.1:8000/api`
- Health check: `http://127.0.0.1:8000/api/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

The first use of T5-small or BART may download model files from Hugging Face if they are not already cached locally.

### 4. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

### 5. Start the frontend

```bash
npm run dev
```

Open the local URL displayed by Vite, usually `http://localhost:5173/`.

## API Reference

### `POST /api/summarize`

Generates a summary from the provided text.

**Example request:**

```json
{
  "text": "Enter the text you want to summarize here.",
  "model": "t5",
  "summary_length": "medium"
}
```

Supported models:
- `textrank`
- `t5`
- `bart`

Supported summary lengths:
- `short`
- `medium`
- `long`

**Example response:**

```json
{
  "summary": "Generated summary text.",
  "model": "t5",
  "original_words": 9,
  "summary_words": 3,
  "processing_time_seconds": 1.234
}
```

The response values above are illustrative.

## Running Tests

From the `backend/` directory, activate the virtual environment and run:

```bash
python -m pytest -q
```

## Production Build

From the `frontend/` directory, run:

```bash
npm run build
```

Vite generates the optimized frontend files in `frontend/dist/`.

## Notes

- The backend and frontend run as separate services during development.
- The frontend expects the backend at `http://127.0.0.1:8000/api`.
- Transformer models require additional memory and disk space compared with the extractive TextRank implementation.
- The frontend production build does not deploy the backend automatically.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details, if present.
