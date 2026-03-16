from General_RAG.insertion_data import QudrantOperation
from Knowledge_Graph.app.services.grpah_build import build_graph
from PageIndex_Logic.pageindex.page_index import page_index_main
from types import SimpleNamespace as config
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator
import os
import json

class insertion_data():
    def __init__(self):
        self.qudrant_operation = QudrantOperation()
    
    def enter_data_for_general_rag(self, pdf_path):
        print("--General RAG Staretd")
        self.qudrant_operation.create_chunks(pdf_path)
        print("--General RAG Completed")
        return True
    
    def enter_data_for_knowledge_graph(self, pdf_path):
        print("---Knowledge Graph Staretd")
        build_graph(pdf_path)
        print("---Knowledge Graph Completed")
        return True

    def enter_data_for_page_index(self, pdf_path):
        print("Page Index Staretd")
        if pdf_path:
            # Validate PDF file
            if not pdf_path.lower().endswith('.pdf'):
                raise ValueError("PDF file must have .pdf extension")
            if not os.path.isfile(pdf_path):
                raise ValueError(f"PDF file not found: {pdf_path}")
                
            # Process PDF file
            # Configure options
            opt = config(
                model="gpt-oss:120b",
                toc_check_page_num=20,
                max_page_num_each_node=10,
                max_token_num_each_node=20000,
                if_add_node_id='yes',
                if_add_node_summary='yes',
                if_add_doc_description='no',
                if_add_node_text='no'
            )

            # Process the PDF
            toc_with_page_number = page_index_main(pdf_path, opt)
            print('Parsing done, saving to file...')
            
            # Save results
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]    
            output_dir = 'PageIndex_Logic/results'
            output_file = f'{output_dir}/{pdf_name}_structure.json'
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(toc_with_page_number, f, indent=2)
            
            print(f'Tree structure saved to: {output_file}')
        print("Page Index Completed")
        return True
        
    def enter_data_for_all(self, pdf_path):
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.enter_data_for_general_rag, pdf_path),
                executor.submit(self.enter_data_for_knowledge_graph, pdf_path),
                executor.submit(self.enter_data_for_page_index, pdf_path)
            ]

            for future in futures:
                future.result()

if __name__ == "__main__":
    insertion = insertion_data()
    # insertion.enter_data_for_general_rag("sample.pdf")
    insertion.enter_data_for_knowledge_graph("sample.pdf")
    # insertion.enter_data_for_page_index("sample.pdf")