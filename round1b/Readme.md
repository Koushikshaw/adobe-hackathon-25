# Round 1B: Persona-Driven Document Intelligence

## Methodology

This solution extracts and ranks document sections from a collection of PDFs based on their relevance to a given user persona and their specific task. [cite_start]The core of this system is built on **semantic search** principles, designed to run entirely offline and on a CPU, respecting the hackathon constraints[cite: 151, 155].

Our approach can be broken down into four key steps:

1.  **Modular Document Segmentation**: We first leverage the principles from Round 1A to create a robust document segmenter. Each PDF is broken down into coherent sections based on its structural headings (e.g., the text that follows an H1 or H2 heading). This ensures that the units of text we analyze are meaningful and self-contained, rather than being arbitrary chunks. [cite_start]This code is designed to be modular and reusable[cite: 97].

2.  **Semantic Query Formulation**: The system combines the `persona` description and the `job-to-be-done` task into a single, comprehensive text query. This query acts as the ground truth for what the user is looking for.

3.  **Vector Embedding with Sentence-Transformers**: To understand the *meaning* behind the text, we use the `all-MiniLM-L6-v2` sentence-transformer model. This lightweight model (under 100MB) excels at converting text into dense vector embeddings. We generate one embedding for our semantic query and one for each document section. Because the model is included in the Docker image, this process works entirely offline.

4.  **Cosine Similarity for Relevance Ranking**: The final step is to measure the relevance between the user's query and each document section. We do this by calculating the **cosine similarity** between the query's vector embedding and each section's embedding. A higher similarity score means the section's content is more semantically aligned with the user's needs. [cite_start]The sections are then ranked in descending order of this score to produce the final `importance_rank`[cite: 144].

This methodology provides a highly accurate, fast, and efficient way to "connect what matters" from a large pool of documents directly to a user's specific goals.