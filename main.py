import argparse
from deep_research_agent import DeepResearchAgent

def parse_args():
    parser = argparse.ArgumentParser(description="Run the DeepResearchAgent.")
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument("--depth", type=int, default=2, help="Depth of exploration (default: 2)")
    parser.add_argument(
        "--queries",
        nargs="+",
        required=True,
        help="Initial search queries (provide at least one)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    print("🔧 Starting DeepResearchAgent...")

    args = parse_args()

    agent = DeepResearchAgent(
        topic=args.topic,
        initial_queries=args.queries,
        max_depth=args.depth
    )

    agent.run()
