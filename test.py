from neo4j import GraphDatabase

# ✅ Updated database details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "testproject"  # ✅ Explicitly set to "testproject"

# Connect to Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def test_connection():
    try:
        with driver.session(database=DATABASE) as session:  # ✅ Use correct database
            result = session.run("RETURN 'Connection Successful' AS msg")
            print(result.single()["msg"])
    except Exception as e:
        print("Error:", e)

test_connection()

def get_projects(tx):
    query = """
    MATCH (p:Project)-[r:RELATED_TO]->(other:Project)
    RETURN DISTINCT p.name AS name, p.description AS description, other.name AS related_project
    """
    return list(tx.run(query))

# Run the query test
with driver.session(database=DATABASE) as session:
    projects = session.execute_read(get_projects)

print("🔹 Fetched Projects:")
print(projects)
