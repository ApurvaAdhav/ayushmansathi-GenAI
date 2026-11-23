MODEL_NAME = "all-MiniLM-L6-v2"
model = None


def get_model():
    """
    Load the embedding model with the ONNX backend so PyTorch is not
    imported at runtime.  ONNX Runtime is already a chromadb dependency,
    so it is always available without adding extra packages.

    Falls back to the default (PyTorch) backend if the ONNX backend is
    unavailable, so local development still works without change.
    """
    global model

    if model is None:
        from sentence_transformers import SentenceTransformer

        try:
            model = SentenceTransformer(MODEL_NAME, backend="onnx")
        except Exception:  # noqa: BLE001
            # Older sentence-transformers or no ONNX Runtime — use default.
            model = SentenceTransformer(MODEL_NAME)

    return model


def generate_embeddings(texts):
    embedding_model = get_model()
    embeddings = embedding_model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()
