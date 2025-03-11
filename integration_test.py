import google.generativeai as genai
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# ✅ Load .env file for API Key
load_dotenv()

# ✅ Get API Key from environment
api_key = os.getenv("GOOGLE_API_KEY")

# ✅ Configure Gemini AI
genai.configure(api_key=api_key)

# ✅ Use a working Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # Change if needed

# ✅ Neo4j Database Connection Details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "testproject"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# ✅ Function to Fetch Projects from Neo4j
def get_projects(tx):
    query = """
    MATCH (p:Project)-[r:RELATED_TO]->(other:Project)
    RETURN DISTINCT p.name AS name, p.description AS description, other.name AS related_project
    """
    return list(tx.run(query))

# ✅ Fetch Project Data from Neo4j
with driver.session(database=DATABASE) as session:
    projects = session.execute_read(get_projects)

# ✅ Format Data for Gemini AI
formatted_data = "\n".join([
    f"Project: {p['name']}\nDescription: {p['description']}\nRelated Project: {p['related_project']}\n"
    for p in projects
])

# ✅ Send to Gemini AI for Summarization
def summarize_projects(data):
    prompt = f"Summarize the following project information:\n\n{data}"
    response = model.generate_content(prompt)
    return response.text

summary = summarize_projects(formatted_data)

# ✅ Print AI-Generated Summary
print("\n🔹 Gemini AI Summary:")
print(summary)
