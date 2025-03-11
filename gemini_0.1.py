import google.generativeai as genai
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import time

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Neo4j Configuration
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "testproject"
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Remove existing summaries from Neo4j
def clear_existing_summaries(tx):
    query = "MATCH (p:Project) REMOVE p.summary"
    tx.run(query)

with driver.session(database=DATABASE) as session:
    session.execute_write(clear_existing_summaries)
    print("✅ Removed all existing summaries in Neo4j.")

# Fetch projects without summaries
def get_projects(tx):
    query = """
    MATCH (p:Project)
    WHERE p.summary IS NULL
    RETURN p.name AS name, p.description AS description, 
           p.objectives AS objectives, p.solution AS solution, p.outcome AS outcome
    """
    return list(tx.run(query))

# Generate strict one-sentence summaries
def summarize_projects(projects):
    batch_size = 5
    summaries = {}

    for i in range(0, len(projects), batch_size):
        batch = projects[i:i+batch_size]
        prompt = "\n\n".join([
            f"Project: {p['name']}\nDescription: {p['description']}\nObjectives: {p['objectives']}\nSolution: {p['solution']}\nOutcome: {p['outcome']}"
            for p in batch
        ])

        ai_prompt = f"""
        Summarize each project in **one sentence, max 15 words**.  
        **DO NOT format, structure, or add explanations—just a short, compressed summary.**  

        {prompt}
        """

        response = model.generate_content(ai_prompt, generation_config={"max_output_tokens": 40})  
        summary_list = response.text.strip().split("\n")

        for idx, project in enumerate(batch):
            summaries[project["name"]] = summary_list[idx] if idx < len(summary_list) else "No summary generated."

        time.sleep(2)

    return summaries

# Store summaries in Neo4j
def store_summary(tx, name, summary):
    query = """
    MATCH (p:Project {name: $name})
    SET p.summary = $summary
    """
    tx.run(query, name=name, summary=summary)

# Run summarization
with driver.session(database=DATABASE) as session:
    projects = session.execute_read(get_projects)

    if projects:
        print(f"✅ Processing {len(projects)} projects...")

        summaries = summarize_projects(projects)

        for name, summary in summaries.items():
            print(f"🔹 RAW AI Response for {name}: {summary}")  # ✅ Debugging output
            session.execute_write(store_summary, name, summary)

print("\n✅ All summaries stored in Neo4j. Run this in Neo4j Browser to verify:")
print("MATCH (p:Project) RETURN p.name, p.summary;")
