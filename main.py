import os
import json
import logging
import argparse
from time import sleep
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from serpapi import GoogleSearch
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from newspaper import Article
from storage import create_connection, insert_entry

# Load environment
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_texts(texts: List[str]) -> List[List[float]]:
    vectors = []
    for text in tqdm(texts, desc="Embedding"):
        try:
            response = openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            vectors.append(response.data[0].embedding)
        except Exception as e:
            print(f"Embedding failed: {e}")
            vectors.append([0.0] * 1536)
    return vectors

def cluster_texts(texts: List[str], num_clusters: int = 3) -> Dict[int, List[str]]:
    embeddings = embed_texts(texts)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    clustered = {}
    for i, label in enumerate(labels):
        clustered.setdefault(label, []).append(texts[i])
    return clustered

def save_clusters(clusters: Dict[int, List[str]], file: str = "clusters.json"):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
    logging.info(f"Clusters saved to {file}")


class DeepResearchAgent:
    def __init__(self, topic: str, initial_queries: List[str], max_depth: int, db_conn):
        self.topic = topic
        self.search_queries = initial_queries
        self.max_depth = max_depth
        self.knowledge_base: Dict[int, str] = {}
        self.conn = db_conn
        logging.info(f"Initialized agent for topic: {topic}")

    def scrape_article(self, url: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text.strip()
        except Exception as e:
            logging.warning(f"Could not scrape {url}: {e}")
            return ""

    def summarize(self, text: str) -> str:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Summarize in 1–2 clear sentences."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Summarization failed: {e}")
            return text

    def select_promising_queries(self, queries: List[str]) -> List[str]:
        return queries[:min(5, len(queries))]

    def execute_search(self, query: str) -> List[Dict[str, str]]:
        logging.info(f"Searching: {query}")
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            logging.error("SERPAPI_API_KEY not set.")
            return []
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 5,
            "hl": "en"
        }
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "link": r.get("link", "")
                }
                for r in results.get("organic_results", [])
            ]
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []

    def score_query(self, query: str) -> float:
        try:
            if not self.knowledge_base:
                return 1.0
            kb_embeddings = embed_texts(list(self.knowledge_base.values()))
            query_embedding = embed_texts([query])[0]
            sims = cosine_similarity([query_embedding], kb_embeddings)[0]
            avg_sim = sum(sims) / len(sims)
            return 1.0 - avg_sim
        except Exception as e:
            logging.error(f"Scoring failed: {e}")
            return 0.0

    def add_to_search_queries(self, new_queries: List[str]):
        scored = [(q, self.score_query(q)) for q in new_queries]
        sorted_queries = [q for q, _ in sorted(scored, key=lambda x: x[1], reverse=True)]
        self.search_queries.extend(sorted_queries)
        logging.info(f"Added {len(sorted_queries)} new queries.")

    def run(self):
        for depth in range(1, self.max_depth + 1):
            logging.info(f"--- Depth {depth} ---")
            queries = self.select_promising_queries(self.search_queries)
            for query in queries:
                results = self.execute_search(query)
                for res in results:
                    title = res.get("title", "")
                    url = res.get("link", "")
                    snippet = res.get("snippet", "")
                    raw_text = self.scrape_article(url) or snippet
                    full_text = f"{title}: {raw_text}"
                    summary = self.summarize(full_text)
                    idx = len(self.knowledge_base) + 1
                    self.knowledge_base[idx] = summary
                    insert_entry(self.conn, title, url, raw_text, summary, None, depth)
                    sleep(1)
                new_queries = [f"More on {res.get('title', '')[:50]}" for res in results]
                self.add_to_search_queries(new_queries)
        logging.info("Research complete.")

    def save_report(self):
        report = f"# Research Report: {self.topic}\n\n## Entries:\n"
        for idx, summary in self.knowledge_base.items():
            report += f"{idx}. {summary}\n"
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        logging.info("Saved report.md")

    def save_knowledge_base(self):
        with open("knowledge.json", "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        logging.info("Saved knowledge.json")


def parse_args():
    parser = argparse.ArgumentParser(description="DeepResearchAgent CLI")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--queries", nargs="+", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    conn = create_connection()

    agent = DeepResearchAgent(args.topic, args.queries, args.depth, conn)
    agent.run()

    # Save report and JSON
    agent.save_report()
    agent.save_knowledge_base()

    # Cluster and save
    clusters = cluster_texts(list(agent.knowledge_base.values()), num_clusters=3)
    save_clusters(clusters)
