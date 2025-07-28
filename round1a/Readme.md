# Round 1A: Document Outline Extractor

This solution extracts a structured outline (Title, H1, H2, H3) from PDF files.

## Approach 

The solution uses a rule-based approach powered by the `PyMuPDF` library. It avoids hard-coded logic by dynamically analyzing the font styles within each document.

1.  **Style Analysis**: The script first scans the PDF to find all unique font sizes and styles (e.g., bold). It counts their occurrences to identify the most common styles.
2.  **Hierarchy Assignment**: The identified styles are sorted in descending order of font size. The largest, most common styles are assumed to be H1, H2, and H3 headings.
3.  **Extraction**: The script then iterates through the document, tagging text that matches these heading styles with their appropriate level (H1, H2, H3) and page number.
4.  **JSON Output**: The final output is structured into the required JSON format, including the document title and a hierarchical list of headings.

## Libraries Used

* **PyMuPDF**: A high-performance Python library for data extraction from PDFs.

## How to Build and Run

### Build the Docker Image

Use the following command to build the image, as specified in the hackathon guidelines. Replace `mysolutionname:somerandomidentifier` with your desired image name.

```sh
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .