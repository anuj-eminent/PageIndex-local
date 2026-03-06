from General_RAG.query_rag import RAGQuery

rag = RAGQuery(model_name="gpt-oss:120b") 

rag.ask_question("What is the capital of France?")  