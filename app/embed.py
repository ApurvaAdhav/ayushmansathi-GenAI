from sentence_transformers import SentenceTransformer
from app.chunking import create_chunks

# Load the pre-trained embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts):
    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    return embeddings.tolist()


if __name__ == "__main__":
    chunks = create_chunks()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)

    print("Total chunks:", len(chunks))
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))
    print("\nFirst embedding:")
    print(embeddings[0][:10])
