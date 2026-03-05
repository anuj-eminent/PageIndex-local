import asyncio
import os
import sys
# Add parent directory to sys.path
sys.path.append(os.getcwd())

from query_structure import load_results, flatten_structure, identify_relevant_nodes, answer_question

async def test_query_logic():
    print("Starting Query Logic Test...")
    
    # Use an existing result file if available
    results_dir = "./results"
    files = [f for f in os.listdir(results_dir) if f.endswith("_structure.json")]
    
    if not files:
        print("No result files found. Skipping test.")
        return

    test_file = os.path.join(results_dir, files[0])
    print(f"Testing with: {test_file}")
    
    data = load_results(test_file)
    structure = data.get("structure", [])
    flat_nodes = flatten_structure(structure)
    print(f"Flattened {len(flat_nodes)} nodes.")
    
    query = "What is the main topic of this document?"
    model = "gpt-oss:120b"
    
    print(f"Identifying relevant nodes for query: '{query}'")
    relevant_ids = await identify_relevant_nodes(query, flat_nodes, model)
    print(f"Relevant IDs: {relevant_ids}")
    
    if relevant_ids:
        # Collect summaries
        context_parts = []
        for node_id in relevant_ids:
            for node in flat_nodes:
                if node["node_id"] == node_id:
                    context_parts.append(f"Section: {node['title']}\nSummary: {node['summary']}")
                    break
        
        context = "\n\n".join(context_parts)
        print("Generating answer...")
        answer = await answer_question(query, context, model)
        print(f"\nAnswer:\n{answer}\n")
        print("Logic test completed successfully.")
    else:
        print("No relevant nodes identified. Test finished.")

if __name__ == "__main__":
    asyncio.run(test_query_logic())
