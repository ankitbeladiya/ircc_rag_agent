import os
import json
import random
import uuid
import subprocess
import sys

# Configuration
SOURCE_DIR = os.path.expanduser("~/project/ircc_rag_agent/notebook/documents")
DEST_DIR = os.path.expanduser("~/project/ircc_rag_agent/notebook/test_set")
MODEL = "qwen3:8b"  # Ensure this model is pulled in ollama
MAX_DOCS = 300

def generate_query(text):
    """
    Generates a realistic user query based on the text using Ollama.
    Truncates text to 2000 chars to fit context window/speed.
    """
    # Prompt engineering specifically for RAG retrieval
    system_prompt = (
        "You are a test data generator. "
        "Output ONLY the final user query. "
        "Do not include any thinking, reasoning, chain-of-thought, or introductory text. "
        "Do not wrap the output in quotes."
    )
    
    user_prompt = (
        "Generate ONE specific, realistic user question based on the text below. "
        "The question must be answerable using ONLY this text. "
        f"Text: {text[:3000]}"
    )
    
    try:
        # Run ollama as a subprocess
        # We combine system and user prompt for the CLI
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        result = subprocess.run(
            ["ollama", "run", MODEL, full_prompt],
            capture_output=True, 
            text=True, 
            check=True
        )
        # Clean up any potential markdown or whitespace
        cleaned = result.stdout.strip().replace('"', '').replace("'", "")
        # aggressive cleanup if model still chats: take last line if multi-line? 
        # usually Qwen is good with "Output ONLY" but let's be safe.
        if "\n" in cleaned:
             # If it output multiple lines, it might be reasoning. 
             # Heuristic: Take the last non-empty line or the longest line?
             # Let's trust the prompt first, but maybe log it.
             lines = [L for L in cleaned.split('\n') if L.strip()]
             if lines:
                 cleaned = lines[-1] # Valid assumption if CoT comes first
        
        return cleaned
    except subprocess.CalledProcessError as e:
        print(f"Error generating query for chunk: {e}", file=sys.stderr)
        return None

def main():
    # 1. Setup Directories
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created directory: {DEST_DIR}")

    # 2. Select Files
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        return

    all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.json')]
    
    if not all_files:
        print("No JSON files found in source directory.")
        return

    # Sort to ensure deterministic order if we use slicing, or seed for random
    all_files.sort()
    
    # Use a fixed seed for reproducibility so we can resume
    random.seed(42)

    # Random sample up to MAX_DOCS
    num_to_process = min(len(all_files), MAX_DOCS)
    selected_files = random.sample(all_files, num_to_process)

    print(f"Found {len(all_files)} files. Selected {len(selected_files)} for processing.", flush=True)

    # 3. Process
    success_count = 0
    skipped_count = 0

    for i, filename in enumerate(selected_files):
        src_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(DEST_DIR, filename)
        
        # SKIP if already exists to resume
        if os.path.exists(dest_path):
            print(f"Skipping {filename}: already exists.", flush=True)
            success_count += 1 # Count as success since we don't need to redo it
            continue

        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            page_content = data.get('page_content', '')
            if not page_content or len(page_content.strip()) < 50:
                print(f"Skipping {filename}: content too short.", flush=True)
                skipped_count += 1
                continue

            print(f"[{i+1}/{len(selected_files)}] Generating query for {filename}...", flush=True)
            
            query = generate_query(page_content)
            
            if not query:
                print(f"Failed to generate query for {filename}", flush=True)
                skipped_count += 1
                continue

            # Construct Golden Set Object
            output_obj = {
                "query_id": str(uuid.uuid4()),
                "query": query,
                "expected_documents": [
                    {
                        "doc_id": data.get('doc_id'),
                        "page_content": page_content,
                        "metadata": data.get('metadata', {})
                    }
                ]
            }

            # Write Output
            with open(dest_path, 'w', encoding='utf-8') as f:
                json.dump(output_obj, f, indent=2, ensure_ascii=False)
            
            print(f"Saved {dest_path}", flush=True)
            success_count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}", flush=True)
            skipped_count += 1

    # 4. Final Report
    print("-" * 50, flush=True)
    print(f"Execution Complete.", flush=True)
    print(f"Success: {success_count} files (including existing).", flush=True)
    print(f"Skipped: {skipped_count} files.", flush=True)
    print(f"Output Directory: {DEST_DIR}")
    print("-" * 50)

if __name__ == "__main__":
    main()
