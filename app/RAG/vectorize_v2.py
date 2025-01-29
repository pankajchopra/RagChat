import os
import numpy as np

from app.RAG.lanchain_faiss_persistence import LangchainFAISSIndexManager
from app.RAG.langchain_and_other_chunking import Chunking
from semantic_search import SemanticSearch
from sklearn.preprocessing import normalize
from pdf_extractions_v2 import PdfExtractions_v2
import tensorflow_hub as hub

chunking = Chunking()


# Function to extract text from a website

def vectorize_and_save(_text_data, _index_path, chunk_data_path="chunks.txt"):
    chunks = chunking.chunk_recursive_character_text_splitter_text(_text_data, chunk_size=1000, chunk_overlap=200)

    # Save chunks to a file
    with open(chunk_data_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk.page_content + "\n")

    cleaned_chunks = []
    # smaller_chunks = []
    semantic_search = SemanticSearch()
    # for chunk in chunks:
    #     smaller_chunks.extend(semantic_search.divide_string_by_words(chunk, num_parts=3))

    for chunk in chunks:
        cleaned_chunks.append(semantic_search.preprocess_text(chunk.page_content))

    local_model_dir = ".\\..\\..\\models\\universal_sentence_encoder"
    # embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
    # embed = hub.load(local_model_dir)
    # embedding_matrix = embed(cleaned_chunks)  # Generate embeddings
    # embedding_matrix = embedding_matrix.numpy()  # Convert to NumPy for FAISS
    # embedding_matrix = np.array(embedding_matrix)  # Ensure it's in NumPy array format
    # embedding_matrix = normalize(embedding_matrix, axis=1)
    faiss_index_manager = LangchainFAISSIndexManager(local_model_dir)
    # Initialize FAISS index
    # if os.path.exists(_index_path):
    faiss_index_manager.create_index(cleaned_chunks);
    faiss_index_manager.save_index_v2(os.path.dirname(__file__) + "/", "faiss_index")
    # if os.path.exists(_index_path) or os.path.exists(os.path.dirname(__file__) + "/" + _index_path):
    #     index = faiss.read_index(os.path.dirname(__file__) + "/" + _index_path)
    #     index.reset()
    #     index = faiss.IndexFlatIP(512)
    #     # Add vectors to FAISS index
    #     index.add(embedding_matrix)
    # else:
    #     embedding_matrix = embedding_matrix.shape[1]
    #     index = faiss.IndexFlatIP(512)
    #     index = index.add(embedding_matrix)  # L2 similarity

    # Save FAISS index to disk
    # faiss.write_index(index, _index_path)

    return len(chunks)


if __name__ == "__main__":
    index_path = "faiss_index.index"
    input_type = "pdf"  # input("Enter input type (pdf/website): ").strip().lower()
    project_root = os.path.dirname(os.path.abspath(__file__))
    if input_type == "pdf":
        pdf_extractions = PdfExtractions_v2("sec_financial_advisor.pdf")
        # pdf_path = input("Enter PDF file path: ").strip()
        pdf_path = "sec_financial_advisor.pdf"
        text_data = pdf_extractions.extract_text_from_pdf(pdf_path)
    elif input_type == "website":
        url = input("Enter website URL: ").strip()
        text_data = chunking.extract_plan_text_from_website(url)
    else:
        print("Invalid input type.")
        exit()

    chunks_count = vectorize_and_save(text_data, index_path)
    print(f"Successfully vectorized {chunks_count} chunks and saved to {index_path}.")
