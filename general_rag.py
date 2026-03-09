from General_RAG.query_rag import RAGQuery

rag = RAGQuery(model_name="gpt-oss:120b") 

def generate_reply(question):
    return rag.ask_question(question)