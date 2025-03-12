import google.generativeai as genai
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import time

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-lite")  # Using the correct model

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

# Fetch all projects (with or without summaries)
def get_projects(tx):
    query = """
    MATCH (p:Project)
    WHERE p.summary IS NULL
    RETURN p.name AS name, p.description AS description, 
           p.objectives AS objectives, p.solution AS solution, 
           p.outcome AS outcome, p.elementId AS elementId
    """
    return list(tx.run(query))

# Generate strict one-sentence summaries
def summarize_projects(projects):
    summaries = {}

    for project in projects:
        print(f"Processing project {project['name']}...")  # Debugging output
        prompt = f"""
        Project: {project['name']}
        Description: {project['description']}
        Objectives: {project['objectives']}
        Solution: {project['solution']}
        Outcome: {project['outcome']}
        
        Summarize this project in one sentence (max 15 words):
        """
        
        try:
            # Get the AI-generated summary
            response = model.generate_content(prompt, generation_config={"max_output_tokens": 40})
            summary = response.text.strip() if response.text else "No summary generated."
            summaries[project['elementId']] = summary  # Use elementId to track projects

        except Exception as e:
            print(f"❌ Error generating summary for {project['name']}: {str(e)}")
            summaries[project['elementId']] = "Error generating summary"

    return summaries

# Store summaries in Neo4j using elementId
def store_summary(tx, element_id, summary):
    query = """
    MATCH (p:Project) WHERE p.elementId = $element_id
    SET p.summary = $summary
    """
    tx.run(query, element_id=element_id, summary=summary)

# Run summarization
with driver.session(database=DATABASE) as session:
    projects = session.execute_read(get_projects)

    if projects:
        print(f"✅ Processing {len(projects)} projects...")

        summaries = summarize_projects(projects)

        for element_id, summary in summaries.items():
            print(f"🔹 AI Summary for ElementId {element_id}: {summary}")  # ✅ Debugging output
            session.execute_write(store_summary, element_id, summary)

# Final message with Neo4j query
print("\n✅ All summaries stored in Neo4j. Run this in Neo4j Browser to verify:")
print("MATCH (p:Project) RETURN p.name, p.summary;")
