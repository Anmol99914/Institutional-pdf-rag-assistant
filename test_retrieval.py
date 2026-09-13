from src.indexer import load_existing_index
from src.embeddings import embed_query
from src.llm import generate_answer
from src.rag import answer_question

vector_store = load_existing_index('vector_store/faiss.index', 'vector_store/metadata.pkl')
result = answer_question('What is Remote Procedure Call in distributed systems?', vector_store, embed_query, generate_answer, top_k=3)
print(result['answer'])
print('low_confidence:', result['low_confidence'])
print('sources:', result['sources'])
