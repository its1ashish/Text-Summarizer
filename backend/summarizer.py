
from functools import lru_cache

import nltk

nltk.download("punkt_tab", quiet=True)

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from transformers import pipeline


# Keep the existing TextRank implementation.
def extractive_summary(text, num_sentences=3):
    parser = PlaintextParser.from_string(
        text,
        Tokenizer("english")
    )
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, num_sentences)

    return " ".join(str(sentence) for sentence in summary)


# Load a transformer model only when it is first requested.
@lru_cache(maxsize=2)
def get_summarizer(model):
    if model == "t5":
        return pipeline(
            "summarization",
            model="t5-small"
        )

    if model == "bart":
        return pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )

    raise ValueError("Unsupported abstractive model")


# Preserve the existing abstractive summarization behavior.
def abstractive_summary(
    text,
    model="t5",
    max_len=60,
    min_len=10
):
    summarizer = get_summarizer(model)

    result = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )

    return result[0]["summary_text"]


def generate_summary(text, model, summary_length):
    length_settings = {
        "short": {"min_len": 10, "max_len": 30},
        "medium": {"min_len": 20, "max_len": 60},
        "long": {"min_len": 30, "max_len": 100},
    }

    if summary_length not in length_settings:
        raise ValueError("Invalid summary length")

    settings = length_settings[summary_length]

    if model == "textrank":
        sentence_counts = {
            "short": 2,
            "medium": 3,
            "long": 5,
        }

        return extractive_summary(
            text,
            num_sentences=sentence_counts[summary_length]
        )

    if model == "t5":
        return abstractive_summary(
            text,
            model="t5",
            **settings
        )

    if model == "bart":
        return abstractive_summary(
            text,
            model="bart",
            **settings
        )

    raise ValueError("Unsupported model")
