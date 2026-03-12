from Knowledge_Graph.app.services.neo4j_database import Neo4jKG
from Knowledge_Graph.app.services.extracting_triplates import extract_triples_from_chunk
from Knowledge_Graph.app.services.chunking_documents import chunk_text
from Knowledge_Graph.app.services.text_extractor import extract_text_from_pdf
from Knowledge_Graph.app.services.ans_question import AnswerQuestion

def build_graph(pdf_path: str):
    chunks = chunk_text(extract_text_from_pdf(pdf_path))
    triples = []
    for chunk in chunks:
        triples.extend(extract_triples_from_chunk(chunk))

    print(triples)


    kg = Neo4jKG()

    for t in triples:
        kg.insert_triple(
            t[0].lower(),
            t[1].lower(),
            t[2].lower()
        )

    kg.close()
    print("\n\n\n\n\n Saviung \n\n\n\n\n")
    AnswerQuestion().save_nodes_embedding()