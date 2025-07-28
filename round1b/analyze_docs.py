import fitz  # PyMuPDF
import json
import os
import re
import time
from sentence_transformers import SentenceTransformer, util

# --- Part 1A Logic (Modularized) ---
def segment_document(doc):
    """Segments a PDF into sections based on headings."""
    # A simplified version of 1A's logic for segmentation
    styles = {}
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line:
                        span = line["spans"][0]
                        styles[round(span["size"])] = styles.get(round(span["size"]), 0) + 1
    
    sorted_sizes = sorted(styles.keys(), reverse=True)
    h1_size = sorted_sizes[0] if sorted_sizes else 0
    
    sections = []
    current_section = {"title": "Introduction", "page": 1, "content": ""}
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line:
                        span = line["spans"][0]
                        text = " ".join([s["text"] for s in line["spans"]]).strip()
                        text = re.sub(r'\s+', ' ', text)
                        
                        if round(span["size"]) == h1_size and len(text.split()) < 20: # Heuristic for a heading
                            if current_section["content"]:
                                sections.append(current_section)
                            current_section = {"title": text, "page": page_num + 1, "content": ""}
                        else:
                            current_section["content"] += text + " "
    if current_section["content"]:
        sections.append(current_section)
        
    return sections

# --- Part 1B Main Logic ---
def analyze_documents(config, doc_paths, model):
    """Analyzes documents based on persona and job."""
    
    # 1. Combine persona and job to form a query
    query = f"Persona: {config['persona']['description']}. Job: {config['job_to_be_done']['task']}"
    query_embedding = model.encode(query, convert_to_tensor=True)

    all_sections = []
    
    # 2. Segment all documents and collect sections
    for doc_path in doc_paths:
        doc_name = os.path.basename(doc_path)
        doc = fitz.open(doc_path)
        doc_sections = segment_document(doc)
        for section in doc_sections:
            all_sections.append({
                "document": doc_name,
                "page": section["page"],
                "section_title": section["title"],
                "content": section["content"]
            })

    # 3. Embed all section contents
    section_contents = [sec["content"] for sec in all_sections]
    if not section_contents:
        return []
        
    section_embeddings = model.encode(section_contents, convert_to_tensor=True)

    # 4. Calculate cosine similarity
    similarities = util.cos_sim(query_embedding, section_embeddings)[0]

    # 5. Rank sections
    for i, section in enumerate(all_sections):
        section["importance_score"] = float(similarities[i])
        
    ranked_sections = sorted(all_sections, key=lambda x: x["importance_score"], reverse=True)

    # 6. Format the output
    extracted_sections_output = []
    for rank, sec in enumerate(ranked_sections):
        extracted_sections_output.append({
            "document": sec["document"],
            "page_number": sec["page"],
            "section_title": sec["section_title"],
            "importance_rank": rank + 1
        })
        
    # Sub-section analysis is left as a simplified placeholder per the brief's focus on section ranking
    # For a full solution, this would involve more granular analysis within top sections.
    sub_section_output = [{
        "document": ranked_sections[0]['document'],
        "page_number": ranked_sections[0]['page'],
        "refined_text": ranked_sections[0]['content'][:500] + "..." # Example: snippet of top section
    }] if ranked_sections else []

    return extracted_sections_output, sub_section_output


if __name__ == "__main__":
    start_time = time.time()
    
    INPUT_DIR = "/app/input"
    OUTPUT_DIR = "/app/output"
    CONFIG_FILE = os.path.join(INPUT_DIR, "config.json")
    
    # Load the sentence-transformer model
    # The model is pre-downloaded in the Dockerfile, so this runs offline.
    model = SentenceTransformer('/app/model')
    
    # Load persona and job config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        
    # Find all PDFs in the input directory
    doc_paths = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    # Run the main analysis
    extracted_sections, sub_sections = analyze_documents(config, doc_paths, model)
    
    # Structure the final JSON output [cite: 133]
    output_data = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in doc_paths],
            "persona": config["persona"]["description"],
            "job_to_be_done": config["job_to_be_done"]["task"],
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": extracted_sections,
        "sub_section_analysis": sub_sections
    }
    
    # Write output file
    output_path = os.path.join(OUTPUT_DIR, "analysis_output.json")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Analysis complete in {time.time() - start_time:.2f} seconds.")
    print(f"Output saved to {output_path}")