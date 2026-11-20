
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

model = None


def get_model():
    global model

    if model is None:
        model = SentenceTransformer(MODEL_NAME)

    return model


def generate_embeddings(texts):
    embedding_model = get_model()

    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=True
    )

    return embeddings.tolist()
