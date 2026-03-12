from General_RAG.insertion_data import QudrantOperation
from Knowledge_Graph.app.services.grpah_build import build_graph

class insertion_data():
    def __init__(self):
        self.qudrant_operation = QudrantOperation()
    
    def enter_data_for_general_rag(self, pdf_path):
        self.qudrant_operation.create_chunks(pdf_path)
        return True
    
    def enter_data_for_knowledge_graph(self, pdf_path):
        build_graph(pdf_path)
        return True

if __name__ == "__main__":
    insertion = insertion_data()
    # insertion.enter_data_for_general_rag("sample.pdf")
    insertion.enter_data_for_knowledge_graph("sample.pdf")