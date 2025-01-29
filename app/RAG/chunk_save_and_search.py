import json
import os

from faiss_persistence import FAISSIndexManager
import numpy as np
import tensorflow_hub as hub
from sklearn.preprocessing import normalize

from app.RAG.semantic_search import SemanticSearch
from summarize_models.summarize import Summarize
from app.database import load_env
import logging
from app.search.chatbot import Chatbot

logger = logging.getLogger(__name__)

index_path = "faiss_index_index.faiss"
text_data_path = "faiss_index_data.pkl"


class ChunkSaveAndSearch:
    def __init__(self):
        pass

    def __init__(self, api_key=None, model_name=None, end_point=None):
        if api_key is None or model_name is None or api_key is None:
            load_env()

        # Load Universal Sentence Encoder
        # local_model_dir = "../../models/universal-sentence-encoder"
        local_model_dir = ".\\..\\..\\models\\universal_sentence_encoder"
        # embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        self.embed = hub.load(local_model_dir)
        self.semantic_search = SemanticSearch()
        self.faiss_persistence = FAISSIndexManager()

    # Function to load FAISS index


    # Perform a search query
    def search_faiss(self, query, top_k=5,  threshold: float = 0.5):
        logger.debug(f"Query: {query}")
        processed_query = self.semantic_search.preprocess_text(query)
        FAISSIndexManager.load_index(os.path.dirname(__file__), "faiss_index")

        logger.debug("Vectorize the query")
        # Vectorize the query
        local_model_dir = ".\\..\\..\\models\\universal_sentence_encoder"
        # embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        _embed = hub.load(local_model_dir)
        query_embd_matrix = _embed([processed_query])
        query_embd_matrix = query_embd_matrix.numpy()  # Convert to NumPy for FAISS
        query_embd_matrix = np.array(query_embd_matrix)  # Ensure it's in NumPy array format
        # if query_embd_matrix.ndim == 1:
        #     query_embd_matrix = query_embd_matrix.reshape(1, -1)  # Reshape to 2D for normalization
        normalized_query = normalize(query_embd_matrix, axis=1)

        # Search the FAISS index
        logger.debug("Search the FAISS index")
        result = self.faiss_persistence.search(normalized_query, top_k)
        # similarities, indices = index.search(normalized_query, top_k)
        # results = []
        # for sim, idx in zip(similarities[0], indices[0]):
        #     if idx != -1 and sim > threshold:
        #         # Calculate additional semantic features
        #         query_tokens = set(processed_query.split())
        #         doc_tokens = set(self.get_a_chunk_by_index(idx).split())
        #
        #         # Term overlap score
        #         overlap_score = len(query_tokens & doc_tokens) / len(query_tokens)
        #
        #         # Combined score (cosine similarity + semantic overlap)
        #         combined_score = (sim + overlap_score) / 2
        #
        #         results.append({
        #             'text': self.get_a_chunk_by_index(idx),
        #             'similarity': float(sim),
        #             'overlap_score': float(overlap_score),
        #             'combined_score': float(combined_score)
        #         })

        # Sort by combined score
        # results.sort(key=lambda x: x['combined_score'], reverse=True)
        return result

    # Retrieve chunks from saved text data (mock implementation)
    @staticmethod
    def get_chunk_by_index(indices):
        absIndexPath = os.path.dirname(__file__) + "\\" + text_data_path
        print(absIndexPath)

        # Simulate chunk retrieval from a text file
        if not (os.path.exists(text_data_path) or os.path.exists(absIndexPath)):
            raise FileNotFoundError(f"Text data file {text_data_path} not found!")

        # Load all chunks (one per line)
        with open(absIndexPath, 'r') as file:
            chunks = file.readlines()

        # Return selected chunks
        selected_chunks = [chunks[idx].strip() for idx in indices if idx < len(chunks)]
        return selected_chunks

    @staticmethod
    def get_a_chunk_by_index(indices):
        absIndexPath = os.path.dirname(__file__) + "\\" + text_data_path
        print(absIndexPath)

        # Simulate chunk retrieval from a text file
        if not (os.path.exists(text_data_path) or os.path.exists(absIndexPath)):
            raise FileNotFoundError(f"Text data file {text_data_path} not found!")

        # Load all chunks (one per line)
        with open(absIndexPath, 'r') as file:
            chunks = file.readlines()

        # Return selected chunks
        selected_chunks = chunks[indices]

        return selected_chunks
    def run_query_simulation_with_llama(self):
        query = input("Enter your query: ").strip()
        if not query:
            print("Query cannot be empty.")
            return True
        elif query == "exit":
            return False
        else:
            print("Query:", query)

        # Perform RAG
        print("\nGenerating response with LLAMAo for query and RAG context...")
        llama_response = self.run_query_with_rag_and_then_with_llama(query)

        print("\nLlama Response:")
        print(llama_response)
        return True

    def run_query_simulation_with_pegasus(self, indexPath, textData_path):
        query = input("Enter your query: ").strip()
        if not query:
            print("Query cannot be empty.")
            return True
        elif query == "exit":
            return False
        else:
            print("Query:", query)

        top_chunks = self.perform_rag_search_return_top_chunks(indexPath, query, textData_path)

        # Perform RAG with Gemini Pro
        print("\nGenerating response with Google Pegasus for query and RAG context...")
        # convert top_chunks to string
        top_chunks_str: str = " ".join(top_chunks)
        pegasus_response = Summarize().summarize_text_with_pegasus(top_chunks_str)

        print("\nGoogle Pegasus Response:")
        print(pegasus_response)
        return True

    def run_query_simulation_with_bart(self, indexPath, textData_path):
        query = input("Enter your query: ").strip()
        if not query:
            print("Query cannot be empty.")
            return True
        elif query == "exit":
            return False
        else:
            print("Query:", query)

        top_chunks = self.perform_rag_search_return_top_chunks(indexPath, query, textData_path)

        # Perform RAG with Gemini Pro
        print("\nGenerating response with Google Pegasus for query and RAG context...")
        bart_response = Summarize().summarize_text_with_bart(top_chunks)

        print("\nGoogle Pegasus Response:")
        print(bart_response)
        return True

    def run_query_with_rag_and_then_with_gemini(self, query):
        global index_path, text_data_path
        if not query:
            print("Query cannot be empty.")
            return True
        top_chunks = self.perform_rag_search_return_top_chunks(index_path, query, text_data_path)

        # Perform RAG with Gemini Pro
        print("\nGenerating response with Gemini Pro for query and RAG context...")
        # gemini_response = self.perform_rag_with_gemini(query, top_chunks)

        print("\nGemini Pro Response:")
        return "gemini_response"

    def run_query_with_rag_and_then_with_llama(self, query):
        global index_path, text_data_path
        if not query:
            print("Query cannot be empty.")
            return True
        top_chunks = self.perform_rag_search_return_top_chunks(index_path, query, text_data_path)

        # Perform RAG with llama 3.3
        print("\nGenerating response with llama for query and RAG context...")
        chatbot = Chatbot(model_name=None, groq_api_key=None, llama_end_point=None)
        topChunks = " ".join(top_chunks)
        # Set system context (optional)
        context = f"You are a helpful financial assistant. Use only context from the following text: {topChunks}. Response has to be friendly and bulleted."
        chatbot.set_system_context(context)
        conversation_history = chatbot.chat(query)
        gemini_llama_response = json.dumps(conversation_history, indent=4)
        print("\nLLAMA Pro Response:")
        return gemini_llama_response

    def perform_rag_search_return_top_chunks(self, indexPath, query, textData_path):
        # Search the FAISS index
        print("Searching for relevant results in FAISS...")

        result = self.search_faiss(query,  4)
        # Retrieve top chunks
        print("\nRetrieving top chunks...")
        top_chunks = [r["text"] for r in result]
        print("\nRetrieved Context:")
        chunks = [r["text"] for r in result]
        index = [r["index"] for r in result]

        for idx, chunk in zip(index, chunks):
            print(f"{idx}. {chunk}")
        return top_chunks

    @staticmethod
    def is_valid_dict_string(string):
        try:
            # Check if the result is a dictionary
            return isinstance(string, dict)
        except (ValueError, SyntaxError):
            # If evaluation fails, the string is not a valid dictionary
            return False


if __name__ == "__main__":
    # Ensure the index and data file exist
    if not os.path.exists(index_path) or not os.path.exists(text_data_path):
        print("Index or text data file not found. Ensure the vectorization step is complete.")
        exit()
    chnk = ChunkSaveAndSearch()

    continueQuery = True
    while continueQuery:
        continueQuery = chnk.run_query_simulation_with_llama()
        # continueQuery = run_query_simulation_with_pegasus(index_path, "chunks.txt")
