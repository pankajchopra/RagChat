import os
import faiss
import tensorflow_hub as hub
import google.generativeai as genai

from app.database import load_env
from app.search.gemini_query_engine import GeminiQueryEngine
import logging

logger = logging.getLogger(__name__)

index_path = "faiss_index.index"
text_data_path = "chunks.txt"


def initialize_gemini(api_key=None, model_name=None):
    """ Initialize GeminiQueryEngine with your API key
    Replace with your Gemini Pro API key
    """
    if ((api_key is None or model_name is None)
            and (os.environ.get('GEMINI_API_KEY') is None or os.environ.get('GEMINI_MODEL') is None)):
        load_env()
        api_key = os.environ['GEMINI_API_KEY']
        model_name = os.environ['GEMINI_MODEL']
    genai.configure(api_key=api_key)  # or genai.configure(api_key)
    return genai.GenerativeModel(model_name=model_name)


# Load Universal Sentence Encoder
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")


# Function to load FAISS index
def load_faiss_index(index_file_path):
    absIndexPath = os.path.dirname(__file__) + "/" + index_file_path
    print(absIndexPath)
    if os.path.exists(index_file_path) or os.path.exists(absIndexPath):
        index = faiss.read_index(absIndexPath)
    else:
        raise FileNotFoundError(f"Index file '{index_file_path}' not found!")
    return index


# Perform a search query
def search_faiss(query, _index_path, top_k=5):
    logger.debug(f"Query: {query}")
    index = load_faiss_index(_index_path)

    logger.debug("Vectorize the query")
    # Vectorize the query
    query_vector = embed([query]).numpy()

    # Search the FAISS index
    logger.debug("Search the FAISS index")
    distances, indices = index.search(query_vector, top_k)
    logger.debug(f"distances{distances} and indices{indices} from the FAISS index")
    return distances[0], indices[0]


# def run_query_simulation(index_path):
#     query = input("Enter your query: ").strip()
#
#     # Search the index
#     print("Searching for relevant results...")
#     distances, indices = search_faiss(query, index_path)
#
#     print("\nTop Results:")
#     for rank, (dist, idx) in enumerate(zip(distances, indices)):
#         print(f"{rank + 1}. Chunk ID: {idx}, Distance: {dist}")

#
# if __name__ == "__main__":
#     index_path = "faiss_index.index"
#
#     # Ensure the index exists
#     if not os.path.exists(index_path):
#         print(f"Index file '{index_path}' not found. Run the vectorization script first.")
#         exit()
#
#     run_query_simulation(index_path)


# Retrieve chunks from saved text data (mock implementation)
def get_chunk_by_index(indices):
    absIndexPath = os.path.dirname(__file__) + "\\" + text_data_path
    print(absIndexPath)

    # Simulate chunk retrieval from a text file
    if not(os.path.exists(text_data_path) or os.path.exists(absIndexPath)):
        raise FileNotFoundError(f"Text data file {text_data_path} not found!")

    # Load all chunks (one per line)
    with open(absIndexPath, 'r') as file:
        chunks = file.readlines()

    # Return selected chunks
    selected_chunks = [chunks[idx].strip() for idx in indices if idx < len(chunks)]
    return selected_chunks


def perform_rag_with_gemini(query, context):
    # Prepare the payload for Gemini Pro
    if os.environ['GEMINI_API_KEY'] == "":
        load_env()
    gemini_query_engine = GeminiQueryEngine(os.environ['GEMINI_API_KEY'])

    system_instruction = {

        "parts": [
            {
                "text": "You are a helpful AI assistant designed to provide accurate and relevant information.\n Answer as concisely as possible in less than 256 tokens.\n".join(context)
            }
        ]
    }
    payload = gemini_query_engine.generate_payload(query, system_info=system_instruction)
    response = gemini_query_engine.query_gemini(payload)
    # payload = {
    #             "text": query + "\n" + "\n".join(context)

    # "systemInstruction": {
    #     "role": "system",
    #     "parts": [
    #                 {
    #                     "text": "Answer as concisely as possible in less than 256 tokens."
    #                  },
    #                 {
    #                     "text": "\n".join(context)
    #                 }
    #             ]
    # },
    # "tools": [{}],
    # "generationConfig": {
    #     "temperature": 0.7,
    #     "maxOutputTokens": 256,
    #     "topP": 0.8,
    #     "topK": 40,
    #     "stopSequences": [],
    # },
    # "labels": {
    #     "type": "rag",
    #     "filetype": "pdf"
    # }
    #
    # if is_valid_dict_string(payload):
    #     # Generate response
    #     # response = _geminiModel.generate_content(query+"\n"+"\n".join(context))
    #     response = _geminiModel.generate_content(payload)
    #     return response.text
    # else:
    #     print("Error: Context is not a dictionary.")

    # response = _geminiModel.generate_content(query+"\n"+"\n".join(context))
    # return "Error: Context is not a dictionary."

    return response


def is_valid_dict_string(string):
    try:

        # Check if the result is a dictionary
        return isinstance(string, dict)
    except (ValueError, SyntaxError):
        # If evaluation fails, the string is not a valid dictionary
        return False


def run_query_simulation_with_gemini(indexPath, textData_path, geminiModel):
    query = input("Enter your query: ").strip()
    if not query:
        print("Query cannot be empty.")
        return True
    elif query == "exit":
        return False
    else:
        print("Query:", query)

    top_chunks = perform_rag_search_return_top_chunks(indexPath, query, textData_path)

    # Perform RAG with Gemini Pro
    print("\nGenerating response with Gemini Pro for query and RAG context...")
    gemini_response = perform_rag_with_gemini(query, top_chunks)

    print("\nGemini Pro Response:")
    print(gemini_response)
    return True


def run_query_with_rag_and_then_with_gemini(query):
    global index_path, text_data_path
    if not query:
        print("Query cannot be empty.")
        return True
    top_chunks = perform_rag_search_return_top_chunks(index_path, query, text_data_path)

    # Perform RAG with Gemini Pro
    print("\nGenerating response with Gemini Pro for query and RAG context...")
    gemini_response = perform_rag_with_gemini(query, top_chunks)

    print("\nGemini Pro Response:")
    return gemini_response


def perform_rag_search_return_top_chunks(indexPath, query, textData_path):
    # Search the FAISS index
    print("Searching for relevant results in FAISS...")
    distances, indices = search_faiss(query, indexPath)
    # Retrieve top chunks
    print("\nRetrieving top chunks...")
    top_chunks = get_chunk_by_index(indices)
    print("\nRetrieved Context:")
    for idx, chunk in enumerate(top_chunks, start=1):
        print(f"{idx}. {chunk}")
    return top_chunks


if __name__ == "__main__":
    load_env()
    # File containing the indexed text chunks

    # Ensure the index and data file exist
    if not os.path.exists(index_path) or not os.path.exists(text_data_path):
        print("Index or text data file not found. Ensure the vectorization step is complete.")
        exit()

    model = initialize_gemini(os.environ['GEMINI_API_KEY'])
    continueQuery = True
    while continueQuery:
        continueQuery = run_query_simulation_with_gemini(index_path, "chunks.txt", model)
