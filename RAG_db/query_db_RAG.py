import sqlite3
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ==== Load API key from .env ====
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ==== Custom embedding function using Gemini ====


class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        pass

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result["embedding"])
        return embeddings


# ==== Connect to persistent Chroma storage ====
client = chromadb.PersistentClient(path="chroma_storage")

# ==== Create or get collection ====
collection = client.get_or_create_collection(
    name="employees-db",
    embedding_function=GeminiEmbeddingFunction()
)

# ==== Step 1: Load rows from SQLite ====
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, department, role FROM employees")
rows = cursor.fetchall()
conn.close()

# ==== Step 2: Embed & add rows (only if not already in collection) ====
existing_ids = set(collection.get()["ids"]
                   ) if collection.count() > 0 else set()
new_docs, new_ids = [], []

for row in rows:
    doc_id = str(row[0])
    if doc_id not in existing_ids:
        doc_text = f"Name: {row[1]}, Department: {row[2]}, Role: {row[3]}"
        new_docs.append(doc_text)
        new_ids.append(doc_id)

if new_docs:
    collection.add(documents=new_docs, ids=new_ids)
    print(f"✅ Added {len(new_docs)} new rows to ChromaDB.")
else:
    print("ℹ️ No new rows to add. Using existing embeddings.")

# ==== Step 3: User query ====
query_text = input("Enter your question:")

results = collection.query(query_texts=[query_text], n_results=3)
retrieved_docs = results["documents"][0]

# ==== Step 4: Send context to Gemini ====
context = "\n".join(retrieved_docs)
prompt = f"""
You are given employee records. Use the context to answer the question.

Context:
{context}

Question:
{query_text}
"""

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(prompt)

print("\n=== Answer ===")
print(response.text)
