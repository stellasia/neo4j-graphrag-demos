"""
Requires:

- pip install "neo4j-graphrag[ollama]"
- Ollama running locally

python 1.3.0/ollama_llm_and_embeddings.py
"""

from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.embeddings import OllamaEmbeddings

embedder = OllamaEmbeddings(model="llama3:8b")
print(embedder.embed_query("is the sky really blue?"))

llm = OllamaLLM(model_name="llama3:8b")
print(llm.invoke("Say something"))


"""
pipeline = SimpleKGPipeline(
    llm=llm,
    embedder=embedder,
    # ...
)
"""
