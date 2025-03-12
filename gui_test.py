import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-lite")  

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"
DATABASE = "testproject"
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

root = tk.Tk()
root.title("Project Manager")
root.geometry("600x600")

def get_projects():
    with driver.session(database=DATABASE) as session:
        query = """
        MATCH (p:Project)
        RETURN p.name AS name, p.description AS description, p.elementId AS elementId
        """
        result = session.run(query)
        return list(result)

def display_projects():
    projects_list.delete(0, tk.END)  
    projects = get_projects()
    for project in projects:
        projects_list.insert(tk.END, f"ID: {project['elementId']} | {project['name']}")

def generate_summary(description):
    prompt = f"""
    Project Description: {description}

    Summarize this project in one sentence (max 15 words):
    """
    try:
        response = model.generate_content(prompt, generation_config={"max_output_tokens": 40})
        return response.text.strip() if response.text else "No summary generated."
    except Exception as e:
        messagebox.showerror("Error", f"Error generating summary: {str(e)}")
        return "Error generating summary"

def add_project():
    name = entry_name.get()
    description = entry_description.get()
    objectives = entry_objectives.get()
    solution = entry_solution.get()
    outcome = entry_outcome.get()

    if not name:
        messagebox.showerror("Error", "Project name cannot be empty.")
        return
    
    generated_summary = generate_summary(description)

    summary_text.delete(1.0, tk.END) 
    summary_text.insert(tk.END, generated_summary)  
    summary_window.deiconify()  

    def store_project():
        with driver.session(database=DATABASE) as session:
            query = """
            CREATE (p:Project {name: $name, description: $description, objectives: $objectives,
                               solution: $solution, outcome: $outcome, summary: $summary})
            """
            summary = summary_text.get(1.0, tk.END).strip() 
            session.run(query, name=name, description=description, objectives=objectives,
                        solution=solution, outcome=outcome, summary=summary)
            messagebox.showinfo("Success", "Project added successfully.")
            summary_window.withdraw()  
            display_projects()  
    
    ok_button.config(command=store_project)

def cancel_edit():
    summary_window.withdraw()

label_name = tk.Label(root, text="Project Name:")
label_name.pack()
entry_name = tk.Entry(root)
entry_name.pack()

label_description = tk.Label(root, text="Description:")
label_description.pack()
entry_description = tk.Entry(root)
entry_description.pack()

label_objectives = tk.Label(root, text="Objectives:")
label_objectives.pack()
entry_objectives = tk.Entry(root)
entry_objectives.pack()

label_solution = tk.Label(root, text="Solution:")
label_solution.pack()
entry_solution = tk.Entry(root)
entry_solution.pack()

label_outcome = tk.Label(root, text="Outcome:")
label_outcome.pack()
entry_outcome = tk.Entry(root)
entry_outcome.pack()

add_button = tk.Button(root, text="Add Project", command=add_project)
add_button.pack()

summary_window = tk.Toplevel(root)
summary_window.title("Review Project Summary")
summary_window.geometry("500x300")
summary_window.withdraw()  

summary_label = tk.Label(summary_window, text="Generated Summary:")
summary_label.pack()

summary_text = tk.Text(summary_window, height=6, width=60)
summary_text.pack()

ok_button = tk.Button(summary_window, text="OK", command=None)  
ok_button.pack()

cancel_button = tk.Button(summary_window, text="Cancel", command=cancel_edit)
cancel_button.pack()

projects_list = tk.Listbox(root, width=80, height=10)
projects_list.pack()

display_projects()
root.mainloop()
