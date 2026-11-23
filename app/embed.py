"""
Embedding generation using onnxruntime + tokenizers directly.

This module deliberately does NOT import sentence-transformers or torch.
sentence-transformers 6.x unconditionally imports torch at module level,
which consumes ~400 MB RAM and exceeds Render's 512 MB limit.

Instead, we:
  1. Download the official ONNX export of all-MiniLM-L6-v2 from HuggingFace
     using huggingface_hub (a lightweight HTTP client, no torch needed).
  2. Run inference with onnxruntime (~20 MB RAM).
  3. Tokenize with the tokenizers library (Rust-based, no torch needed).

The resulting embeddings are identical to those produced by
sentence-transformers with the same model — ChromaDB queries still work
correctly because the vector space is unchanged.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"
# Sub-folder inside the HF repo that contains the ONNX export
ONNX_SUBFOLDER = "onnx"
ONNX_FILENAME = "model.onnx"

# Local cache directory (inside the project so Docker COPY picks it up)
_BASE_DIR = Path(__file__).resolve().parent.parent
_MODEL_DIR = _BASE_DIR / "data" / "onnx_model"
_ONNX_PATH = _MODEL_DIR / "onnx" / ONNX_FILENAME
_TOKENIZER_PATH = _MODEL_DIR / "tokenizer.json"

_session = None      # onnxruntime.InferenceSession
_tokenizer = None    # tokenizers.Tokenizer


# ------------------------------------------------------------------
# 1.  Download the ONNX model + tokenizer on first use
# ------------------------------------------------------------------

def _ensure_model() -> None:
    """Download model files from HuggingFace if they are not cached yet."""
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if not _ONNX_PATH.exists() or not _TOKENIZER_PATH.exists():
        from huggingface_hub import hf_hub_download

        print(f"Downloading ONNX model from {MODEL_REPO} ...")

        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=f"{ONNX_SUBFOLDER}/{ONNX_FILENAME}",
            local_dir=str(_MODEL_DIR),
        )

        hf_hub_download(
            repo_id=MODEL_REPO,
            filename="tokenizer.json",
            local_dir=str(_MODEL_DIR),
        )

        hf_hub_download(
            repo_id=MODEL_REPO,
            filename="tokenizer_config.json",
            local_dir=str(_MODEL_DIR),
        )

        print("Model downloaded successfully.")


# ------------------------------------------------------------------
# 2.  Load session and tokenizer (once per process)
# ------------------------------------------------------------------

def _get_session():
    global _session
    if _session is None:
        import onnxruntime as ort

        _ensure_model()
        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1

        _session = ort.InferenceSession(
            str(_ONNX_PATH),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
    return _session


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from tokenizers import Tokenizer

        _ensure_model()
        _tokenizer = Tokenizer.from_file(str(_TOKENIZER_PATH))
        _tokenizer.enable_padding(pad_token="[PAD]", pad_id=0, length=None)
        _tokenizer.enable_truncation(max_length=256)
    return _tokenizer


# ------------------------------------------------------------------
# 3.  Mean pooling (same as sentence-transformers default)
# ------------------------------------------------------------------

def _mean_pool(token_embeddings: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    mask = attention_mask[:, :, np.newaxis].astype(np.float32)
    summed = (token_embeddings * mask).sum(axis=1)
    counts = mask.sum(axis=1).clip(min=1e-9)
    return summed / counts


def _normalise(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True).clip(min=1e-12)
    return vectors / norms


# ------------------------------------------------------------------
# 4.  Public API — same signature as before
# ------------------------------------------------------------------

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Return L2-normalised 384-dim embeddings for each input text.
    Identical output to SentenceTransformer('all-MiniLM-L6-v2').encode().
    """
    tokenizer = _get_tokenizer()
    session = _get_session()

    encodings = tokenizer.encode_batch(texts)

    input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids)

    outputs = session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        },
    )

    # outputs[0] is the last_hidden_state: (batch, seq_len, hidden)
    token_embeddings = outputs[0]
    pooled = _mean_pool(token_embeddings, attention_mask)
    normed = _normalise(pooled)
    return normed.tolist()
