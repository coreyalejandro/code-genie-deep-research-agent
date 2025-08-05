import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from tqdm import tqdm
from sklearn.cluster import KMeans
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI v1+ client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate OpenAI embeddings for each text in the list.
    """
    vectors = []
    for text in tqdm(texts, desc="🔢 Embedding texts"):
        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response.data[0].embedding
            vectors.append(embedding)
        except Exception as e:
            print(f"⚠️ Embedding failed: {e}")
            vectors.append([0.0] * 1536)  # fallback to zero vector
    return vectors


def cluster_texts(texts: List[str], num_clusters: int = 3) -> Dict[int, List[str]]:
    """
    Cluster embedded texts into topic groups using KMeans.
    """
    embeddings = embed_texts(texts)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    clustered = {}
    for idx, label in enumerate(labels):
        clustered.setdefault(label, []).append(texts[idx])
    return clustered


def save_clusters(clustered: Dict[int, List[str]], file_path: str = "clusters.json"):
    """
    Save clustered groups to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clustered, f, ensure_ascii=False, indent=2)
    print(f"✅ Clustered topics saved to {file_path}")
