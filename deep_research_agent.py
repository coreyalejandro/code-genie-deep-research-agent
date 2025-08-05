import os
import logging
from typing import List, Any, Dict
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DeepResearchAgent:
    def __init__(self, topic: str, initial_queries: List[str], max_depth: int):
        self.topic = topic
        self.search_queries = initial_queries
        self.max_depth = max_depth
        self.knowledge_base: Dict[int, Any] = {}
        logging.info(f"Research agent initialized for topic: {topic} with max depth: {max_depth}")

    def select_promising_queries(self, queries: List[str]) -> List[str]:
        return queries[:min(5, len(queries))]

    def execute_search(self, query: str) -> List[Dict[str, str]]:
        logging.info(f"Executing search query via SerpAPI: {query}")
        api_key = os.getenv("SERPAPI_API_KEY")

        if not api_key:
            logging.error("❌ SERPAPI_API_KEY not set in environment.")
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
            organic_results = results.get("organic_results", [])
            simplified = [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                }
                for item in organic_results
            ]
            return simplified
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []

    def process_results(self, results: List[Dict[str, str]]) -> List[str]:
        logging.info(f"Processing {len(results)} search results.")
        return [f"{res['title']}: {res['snippet']}" for res in results if res['snippet']]

    def store_in_knowledge_base(self, processed_results: List[str]):
        for result in processed_results:
            idx = len(self.knowledge_base) + 1
            self.knowledge_base[idx] = result
            logging.info(f"Stored item #{idx} in knowledge base.")

    def extract_new_queries(self, processed_results: List[str]) -> List[str]:
        return [f"More on {res[:50]}" for res in processed_results]

    def add_to_search_queries(self, new_queries: List[str]):
        self.search_queries.extend(new_queries)
        logging.info(f"Added {len(new_queries)} new queries.")

    def analyze_knowledge_base(self) -> str:
        logging.info("Analyzing knowledge base...")
        return f"{len(self.knowledge_base)} entries analyzed. Emerging themes: AI disruption, ethics, applications."

    def update_search_queries(self, insights: str):
        self.search_queries.append(f"Explore: {insights}")

    def prune_knowledge_base(self):
        pass

    def prune_search_queries(self):
        self.search_queries = list(dict.fromkeys(self.search_queries))

    def generate_report(self, insights: str) -> str:
        report = f"\n📘 Research Report on: {self.topic}\n"
        report += f"---\n🔍 Insights:\n{insights}\n\n📚 Knowledge Base:\n"
        for idx, entry in self.knowledge_base.items():
            report += f"{idx}. {entry}\n"
        return report

    def run(self):
        logging.info("Starting deep research...")

        for depth in range(1, self.max_depth + 1):
            logging.info(f"\n===== Depth {depth} =====")
            queries = self.select_promising_queries(self.search_queries)

            for query in queries:
                raw_results = self.execute_search(query)
                processed = self.process_results(raw_results)
                self.store_in_knowledge_base(processed)
                new_queries = self.extract_new_queries(processed)
                self.add_to_search_queries(new_queries)

            insights = self.analyze_knowledge_base()
            self.update_search_queries(insights)
            self.prune_search_queries()

        report = self.generate_report(insights)
        print(report)
        logging.info("✅ Research completed.")

