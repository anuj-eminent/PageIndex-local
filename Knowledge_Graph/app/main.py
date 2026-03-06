from services.text_extractor import extract_text_from_pdf
from services.chunking_documents import chunk_text
from services.grpah_build import build_graph
from services.retrival_graph import Neo4jReader

# data = chunk_text(extract_text_from_pdf('../Set_1/BGEM_Scientific_Reports.pdf'))
# print(data)

build_graph("ans")

# data = Neo4jReader()
# print(data.fetch_relations("Dataset"))