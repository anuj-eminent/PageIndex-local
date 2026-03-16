import os
import json
import asyncio
import argparse
from typing import List, Dict, Any
from PageIndex_Logic.pageindex.llm import get_llm_client
from PageIndex_Logic.pageindex.utils import extract_json

def list_result_files(results_dir: str = "./results") -> List[str]:
    """Lists available result files in the results directory."""
    if not os.path.exists(results_dir):
        return []
    return [f for f in os.listdir(results_dir) if f.endswith("_structure.json")]

def load_results(file_path: str) -> Dict[str, Any]:
    """Loads the processed structure from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_structure(structure: List[Dict[str, Any]], level: int = 0) -> List[Dict[str, Any]]:
    """Flattens the hierarchical structure for easier searching/indexing."""
    flat_list = []
    for node in structure:
        # Create a copy with basic info for retrieval
        node_info = {
            "title": node.get("title"),
            "node_id": node.get("node_id"),
            "summary": node.get("summary"),
            "level": level
        }
        flat_list.append(node_info)
        if "nodes" in node and node["nodes"]:
            flat_list.extend(flatten_structure(node["nodes"], level + 1))
    return flat_list

async def identify_relevant_nodes(query: str, nodes: List[Dict[str, Any]], model: str) -> List[str]:
    """Asks the LLM to identify the most relevant node IDs for a given query."""
    llm = get_llm_client()
    
    # Prepare a condensed list of titles and node_ids for the picker
    choices = "\n".join([f"ID: {n['node_id']} - Title: {n['title']}" for n in nodes])
    
    prompt = f"""
    Given the following document structure (titles and IDs), identify which sections are most relevant to answering this question: "{query}"
    
    Document Structure:
    {choices}
    
    Return a JSON list of relevant Node IDs, ordered by relevance. If no sections are relevant, return an empty list.
    Format:
    {{
        "relevant_ids": ["ID1", "ID2", ...]
    }}
    Directly return the JSON structure. Do not output anything else.
    """
    
    response = await llm.chat_async(model=model, messages=[{"role": "user", "content": prompt}])
    result = extract_json(response)
    return result.get("relevant_ids", [])

async def answer_question(query: str, context: str, model: str) -> str:
    """Generates an answer based on the provided query and context."""
    llm = get_llm_client()
    
    prompt = f"""
    You are an expert assistant. Answer the following question using ONLY the provided document context.
    If the context doesn't contain the answer, say you don't know based on the provided information.
    
    Context:
    {context}
    
    Question: {query}
    
    Answer:
    """
    
    return await llm.chat_async(model=model, messages=[{"role": "user", "content": prompt}])

async def answer_question_from_structure(query: str, structure: List[Dict[str, Any]], model: str) -> str:
    """
    Core function to answer a question given a hierarchical structure.
    Useful for API calls.
    """
    flat_nodes = flatten_structure(structure)
    relevant_ids = await identify_relevant_nodes(query, flat_nodes, model)
    
    context_parts = []
    for node_id in relevant_ids:
        for node in flat_nodes:
            if node["node_id"] == node_id:
                context_parts.append(f"Section: {node['title']}\nSummary: {node['summary']}")
                break
    
    if not context_parts:
        return {"context": context_parts, "answer": "I couldn't find any relevant sections in the document to answer your question."}
        
    context = "\n\n".join(context_parts)
    return {"context": context_parts, "answer": await answer_question(query, context, model)}

async def query_loop(results_dir: str, model: str):
    """Main interactive loop for querying."""
    files = list_result_files(results_dir)
    if not files:
        print(f"No result files found in {results_dir}. Please run run_pageindex.py first.")
        return

    print("\nAvailable processed documents:")
    for i, file in enumerate(files):
        print(f"{i + 1}. {file}")
    
    try:
        choice = int(input(f"\nSelect a document (1-{len(files)}): ")) - 1
        if choice < 0 or choice >= len(files):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a number.")
        return

    file_path = os.path.join(results_dir, files[choice])
    data = load_results(file_path)
    structure = data.get("structure", [])
    flat_nodes = flatten_structure(structure)
    
    print(f"\nLoaded: {data.get('doc_name')}")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        query = input("\nAsk a question: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        if not query:
            continue

        print("Generating answer...")
        answer = await answer_question_from_structure(query, structure, model)
        
        print("\n" + "="*50)
        print(f"Answer:\n{answer}")
        print("="*50)

