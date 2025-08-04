import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ==== Load API Key from .env ====
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# ==== Read and split content from Me.txt ====
file_path = "documents/Me.txt"

# Basic line-by-line chunking (can be improved later)
with open(file_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Simple split (you can use NLP-based chunking for better results)
chunks = raw_text.split("\n\n")  # Paragraph-based split
documents = [
    {"id": f"chunk-{i}", "content": chunk.strip()}
    for i, chunk in enumerate(chunks) if chunk.strip()
]

# ==== Gemini Embedding Function ====
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

embedding_fn = GeminiEmbeddingFunction()

# ==== Initialize ChromaDB and store embeddings ====
client = chromadb.Client()
collection = client.get_or_create_collection(name="rag-docs", embedding_function=embedding_fn)

for doc in documents:
    collection.add(
        documents=[doc["content"]],
        ids=[doc["id"]]
    )

# ==== Query the collection for relevant documents ====
query_text = "Where does Ammar live?"
results = collection.query(query_texts=[query_text], n_results=3)

relevant_docs = [doc for doc in results['documents'][0]]

# Join into single context string
context = "\n".join(relevant_docs)

# ==== Generate response using Gemini Model ====
model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content(
    f"""Use the following context to answer the question.

    Context:
    {context}

    Question:
    {query_text}
    """,
    generation_config={
        "temperature": 0.2,
        "top_k": 5,
        "top_p": 0.95,
        "max_output_tokens": 512,
    },
)

print(response.text)