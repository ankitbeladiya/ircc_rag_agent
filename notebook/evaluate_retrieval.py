import os
import json
from typing import List

# Set the path to where your gold dataset is currently generating
TEST_SET_DIR = "/home/ankit/project/ircc_rag_agent/notebook/test_set/"

def mock_retriever(query: str, k: int) -> List[str]:
    """
    REPLACE THIS FUNCTION WITH YOUR ACTUAL RETRIEVAL PIPELINE.
    It should take the user 'query' and return a list of the top 'k' retrieved 'doc_id' strings.
    """
    # Example: return ["doc_123", "adopt-child-abroad_1_6_0", "doc_456"]
    return []

def calculate_precision_recall_at_k(retrieved_doc_ids: List[str], expected_doc_ids: List[str], k: int):
    """
    Calculates Precision@K and Recall@K.
    """
    # Truncate retrieved to top K
    retrieved_at_k = retrieved_doc_ids[:k]
    
    # Intersection of expected and retrieved
    relevant_retrieved = len(set(retrieved_at_k).intersection(set(expected_doc_ids)))
    
    # Precision: Out of all retrieved, how many were relevant?
    precision = relevant_retrieved / k if k > 0 else 0.0
    
    # Recall: Out of all expected relevant docs, how many did we retrieve?
    recall = relevant_retrieved / len(expected_doc_ids) if len(expected_doc_ids) > 0 else 0.0
    
    return precision, recall

def evaluate_rag_system(k_values=[1, 3, 5]):
    """
    Loops through the test set JSON files and evaluates the retriever.
    """
    metrics = {k: {"precision": [], "recall": []} for k in k_values}
    files_processed = 0
    
    # Loop through the gold dataset directory
    for filename in os.listdir(TEST_SET_DIR):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(TEST_SET_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            query = data.get("query", "")
            
            # Extract expected doc IDs
            expected_docs = data.get("expected_documents", [])
            expected_doc_ids = []
            if expected_docs:
                for doc in expected_docs:
                    # Depending on structure, it might be dict or string. Assuming dict with doc_id from example
                    if isinstance(doc, dict) and "doc_id" in doc:
                        expected_doc_ids.append(doc["doc_id"])
                    elif isinstance(doc, str):
                        expected_doc_ids.append(doc)
            
            if not query or not expected_doc_ids:
                continue

            # --- RUN RETRIEVAL ---
            # Assume we pull the maximum K value needed
            max_k = max(k_values)
            retrieved_doc_ids = mock_retriever(query, k=max_k)
            
            # --- CALCULATE METRICS ---
            for k in k_values:
                p, r = calculate_precision_recall_at_k(retrieved_doc_ids, expected_doc_ids, k)
                metrics[k]["precision"].append(p)
                metrics[k]["recall"].append(r)
                
            files_processed += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Calculate Aggregates
    print(f"\nEvaluating {files_processed} sample queries...")
    if files_processed == 0:
        print("No queries evaluated.")
        return

    for k in k_values:
        avg_precision = sum(metrics[k]["precision"]) / len(metrics[k]["precision"])
        avg_recall = sum(metrics[k]["recall"]) / len(metrics[k]["recall"])
        print(f"--- Top {k} ---")
        print(f"Average Precision@{k}: {avg_precision:.4f}")
        print(f"Average Recall@{k}:    {avg_recall:.4f}")

if __name__ == "__main__":
    # You typically want K=1 (did it get it first try?), 
    # K=3 and K=5 (was it passed to the LLM contextual prompt?)
    evaluate_rag_system(k_values=[1, 3, 5])
