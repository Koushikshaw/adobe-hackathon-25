import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict

def get_font_styles(doc):
    """Analyzes the document to identify common font sizes and flags for headings."""
    styles = defaultdict(int)
    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_FONT)
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line:
                        for span in line["spans"]:
                            # A style is a unique combination of size and bold flag
                            style_key = (round(span["size"]), "bold" in span["font"].lower())
                            styles[style_key] += 1
    
    # Filter out styles that are very infrequent, likely body text or noise
    min_occurrence = 3 # Heuristic: a heading style should appear a few times
    frequent_styles = {k: v for k, v in styles.items() if v >= min_occurrence or k[1]} # Keep all bold styles
    
    # Sort styles by size (desc) and boldness (bold first)
    sorted_styles = sorted(frequent_styles.keys(), key=lambda x: (-x[0], -x[1]))
    
    # Assume the top 3-4 styles are headings H1, H2, H3, and potentially a Title
    return sorted_styles[:4]

def extract_outline(pdf_path):
    """Extracts Title, H1, H2, H3 from a PDF document."""
    doc = fitz.open(pdf_path)
    
    if not doc.page_count:
        return {"title": "", "outline": []}

    # Identify potential heading styles
    heading_styles = get_font_styles(doc)
    
    # Assign H1, H2, H3 based on sorted styles
    style_map = {}
    if len(heading_styles) > 0: style_map[heading_styles[0]] = "H1"
    if len(heading_styles) > 1: style_map[heading_styles[1]] = "H2"
    if len(heading_styles) > 2: style_map[heading_styles[2]] = "H3"
    
    outline = []
    title = os.path.basename(pdf_path) # Fallback title

    # Attempt to find a title on the first page
    first_page_text = doc[0].get_text("blocks")
    if first_page_text:
        # Often the first block of text with the largest font is the title
        title = first_page_text[0][4].strip().replace('\n', ' ')

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_FONT)["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if "spans" in line and line["spans"]:
                        span = line["spans"][0]
                        text = " ".join([s["text"] for s in line["spans"]]).strip()
                        
                        # Clean up common PDF text issues
                        text = re.sub(r'\s+', ' ', text)
                        if not text:
                            continue

                        span_style = (round(span["size"]), "bold" in span["font"].lower())
                        
                        if span_style in style_map:
                            level = style_map[span_style]
                            outline.append({
                                "level": level,
                                "text": text,
                                "page": page_num + 1
                            })
                            
    return {"title": title, "outline": outline}


if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            output_data = extract_outline(pdf_path)
            
            json_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, json_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            
            print(f"Processed {filename}, output saved to {json_filename}")