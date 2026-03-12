from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    embedding = model.encode(text)
    return embedding


if __name__ == "__main__":
    text_input = "B.Tech student at Birla Vishvakarma Mahavidyalaya with a focus on Deep Learning."
    vector = get_embedding(text_input)

    print(f"Task Complete. Vector Dimension: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")