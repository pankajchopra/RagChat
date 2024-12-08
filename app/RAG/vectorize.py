import os
import re
import faiss
import nltk

from pdf_extractions import PdfExtractions

# nltk.download('punkt')
nltk.download('punkt_tab')
import tensorflow_hub as hub
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import requests
from utils import clean_text

# Load Universal Sentence Encoder (USE)
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
# "https://ai.google.dev/gemini-api/docs/system-instructions?lang=python"




# Function to extract text from a website
def extract_text_from_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.text for p in soup.find_all('p')])
    """Removes non-printable characters from a string."""
    printable_chars = set(text.printable)
    text = ''.join(c for c in text if c in printable_chars)
    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z]", " ", text)
    return text


# Chunking Function
def chunk_text(text, max_length=256):
    words = text.split()
    chunks = [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]
    return chunks


def chunk_section_wise_text(structured_resume6):
    # chunks = [list(d.keys())[0] + ":" + list(d.values())[0] for d in structured_resume6]
    chunks = [f"{key}:{value}" for key, value in structured_resume6.items()]
    return chunks



# Sentence based Chunking Function
def chunk_senetence_based_text(text, max_length=512):
    sentences = nltk.sent_tokenize(text)
    return sentences


# Hybrid  Chunking Function
def hybrid_chunking(text, max_tokens_per_chunk):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        if current_tokens + len(tokens) <= max_tokens_per_chunk:
            current_chunk.append(sentence)
            current_tokens += len(tokens)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = len(tokens)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def vectorize_and_save(text_data, index_path,  chunk_data_path="chunks.txt"):
    # chunks = chunk_senetence_based_text(text_data, max_length=256)
    # chunks = hybrid_chunking(text_data, max_tokens_per_chunk=1024)
    chunks = chunk_section_wise_text(text_data)

    # Save chunks to a file
    with open(chunk_data_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk + "\n")

    vectors = embed(chunks)  # Generate embeddings
    vectors = vectors.numpy()  # Convert to NumPy for FAISS

    # Initialize FAISS index
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        dimension = vectors.shape[1]
        index = faiss.IndexFlatL2(dimension)  # L2 similarity

    # Add vectors to FAISS index
    index.add(vectors)
    faiss.write_index(index, index_path)
    return len(chunks)


if __name__ == "__main__":
    index_path = "faiss_index.index"
    input_type = "pdf"  # input("Enter input type (pdf/website): ").strip().lower()

    if input_type == "pdf":
        pdf_extractions = PdfExtractions()
        pdf_path = input("Enter PDF file path: ").strip()
        text_data = pdf_extractions.extract_text_by_sections(pdf_path)
    elif input_type == "website":
        url = input("Enter website URL: ").strip()
        text_data = extract_text_from_website(url)
    else:
        print("Invalid input type.")
        exit()

    chunks_count = vectorize_and_save(text_data, index_path)
    print(f"Successfully vectorized {chunks_count} chunks and saved to {index_path}.")
