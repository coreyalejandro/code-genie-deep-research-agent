from deep_research_agent import DeepResearchAgent

print("🔧 Starting DeepResearchAgent...")

if __name__ == "__main__":
    topic = "The future of AI"
    initial_queries = [
        "Future trends in artificial intelligence",
        "AI and job automation",
        "Ethical concerns of AI",
        "AI in healthcare",
        "AGI vs narrow AI"
    ]
    max_depth = 2

    agent = DeepResearchAgent(topic, initial_queries, max_depth)
    agent.run()
