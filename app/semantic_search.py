import json
import os
import re
from typing import List

import faiss
import nltk
import numpy as np
import tensorflow_hub as hub
from sklearn.preprocessing import normalize

from app.RAG.lanchain_faiss_persistence import LangchainFAISSIndexManager
from app.search.chatbot import Chatbot
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.data.path.append('../../models/nltk_data')


class SemanticSearch:
    def __init__(self, dimension: int = 512):
        """
        Initialize semantic search with Universal Sentence Encoder and FAISS

        Args:
            dimension: Embedding dimension (512 for USE-large)
        """
        # Download required NLTK data no need point to the local directory
        # nltk.download('punkt')
        # nltk.download('stopwords')
        # nltk.download('wordnet')

        # Initialize NLP tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        local_model_dir = ".\\..\\..\\models\\universal_sentence_encoder"
        # Load Universal Sentence Encoder
        # self.encoder = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
        self.encoder = hub.load(local_model_dir)

        # Initialize FAISS index with L2 normalization
        self.index = faiss.IndexFlatIP(dimension)  # Using Inner Product distance

        self.texts = []
        self.processed_texts = []

    def preprocess_text(self, text: str) -> str:
        """
             Preprocess text with enhanced hyphen handling
             """
        # Handle hyphens first
        print(f"Original text of length {len(text)}")
        text = self.handle_hyphens(text)

        # Tokenization
        tokens = word_tokenize(text.lower())

        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token)
                  for token in tokens
                  if token.isalnum() and token not in self.stop_words]

        return ' '.join(tokens)

    def compute_embedding(self, texts: List[str]) -> np.ndarray:
        """
        Compute normalized embeddings for texts
        """
        embeddings = self.encoder(texts).numpy()
        # L2 normalize embeddings for cosine similarity
        return normalize(embeddings)

    def add_documents(self, documents: List[str]) -> None:
        """
        Add documents to the index with semantic preprocessing
        """
        # Store original texts
        self.texts.extend(documents)

        # Preprocess documents
        processed_docs = [self.preprocess_text(doc) for doc in documents]
        self.processed_texts.extend(processed_docs)

        # Create normalized embeddings
        embeddings = self.compute_embedding(processed_docs)
        self.index.add(embeddings)


    def semantic_search_v2(self, query: str, top_k: int = 5):
        faiss_persistence_manager = LangchainFAISSIndexManager(".\\..\\..\\models\\universal_sentence_encoder")
        faiss_persistence_manager.load_index_v2(os.path.dirname(__file__), "faiss_index")
        return faiss_persistence_manager.similarity_search(query, top_k)

    def semantic_search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[tuple]:
        """
        Perform semantic search with enhanced matching

        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity score threshold

        Returns:
            List of tuples containing (text, similarity_score, semantic_match)
        """
        # Preprocess query
        processed_query = self.preprocess_text(query)

        # Create normalized query embedding
        query_embedding = self.compute_embedding([processed_query])
        normalized_query = normalize(query_embedding)

        # Search index using cosine similarity
        similarities, indices = self.index.search(normalized_query, top_k)

        # Prepare results with semantic matching
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx != -1 and sim > threshold:
                # Calculate additional semantic features
                query_tokens = set(processed_query.split())
                doc_tokens = set(self.processed_texts[idx].split())

                # Term overlap score
                overlap_score = len(query_tokens & doc_tokens) / len(query_tokens)

                # Combined score (cosine similarity + semantic overlap)
                combined_score = (sim + overlap_score) / 2

                results.append({
                    'text': self.texts[idx],
                    'similarity': float(sim),
                    'overlap_score': float(overlap_score),
                    'combined_score': float(combined_score)
                })

        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        return results

    def handle_hyphens(self, text: str) -> str:
        """
        Process hyphenated words to create multiple variations
        """
        # Find all hyphenated words
        hyphenated_words = re.findall(r'\w+(?:-\w+)+', text)

        processed_text = text
        for word in hyphenated_words:
            variations = []
            # Original hyphenated form
            variations.append(word)

            # Form without hyphens
            no_hyphen = word.replace('-', '')
            variations.append(no_hyphen)

            # Form with spaces instead of hyphens
            space_separated = word.replace('-', ' ')
            variations.append(space_separated)

            # Split into individual words
            individual_words = word.split('-')
            variations.extend(individual_words)

            # Replace original word with all variations
            processed_text = processed_text.replace(
                word,
                ' '.join(variations)
            )

        return processed_text

    def divide_string_by_words(self, long_string, num_parts=3):
        words = long_string.split()  # Split the string into words
        total_words = len(words)
        part_size = total_words // num_parts  # Approximate size of each part

        parts = []  # To store the divided parts
        start = 0  # Starting index of each part

        for i in range(num_parts - 1):  # For the first (num_parts - 1) parts
            if start != 0:
                start = start - 5
            end = start + part_size
            # Adjust end to the closest word boundary
            parts.append(" ".join(words[start:end]))
            start = end

        # Add the remaining words as the last part
        parts.append(" ".join(words[start:]))
        return parts

    def perform_rag_and_llm_search(self, query):
        query_top = query
        # Initialize search engine
        search_engine = SemanticSearch()

        llm_chatbot: Chatbot = Chatbot();
        context = '''You are a helpful financial assistant. contents sent by the user role 
                        Provide revised versions of queries and make it relevant so that it can search in the Financial Advisor regulation of SEC. here is the query to fix 
                        "in JSON format with the following structure ( very strictly) just one element in the json named 'revisedQuery' here is the example, '{"revisedQuery": ["revised query 1", "revised query 2", , "revised query 2"]}
                        Make sure the response is concise and to the point what is asked'''
        llm_chatbot.set_system_context(context)
        # Perform a search
        # query_top = "Mid-Size advisers large size advisers tell me more what is difference between mid, small and large size advisers in dollar terms"
        # query_top = "Who is an Investment Adviser? I want to know what he can do for me tell me 5 most important in very brief bullets"
        llm_response = llm_chatbot.chat(query_top, revisedQuery=True)
        print(llm_response)
        response1 = json.loads(json.dumps(llm_response))
        json_response_list = [item['content'] for item in response1 if item['role'] == 'assistant']
        json_response_objects = json_response_list[0]["content"]
        # Extract the list from the dictionary
        query_list_object = json.loads(json_response_objects)
        query_list = query_list_object["revisedQuery"]
        chunks_from_rag = []
        # Iterate over the list
        for query_top in query_list:
            results = search_engine.semantic_search_v2(query_top, top_k=3)
            chunks_from_rag.extend(results)

        # Sort results by similarity score in descending order
        chunks_from_rag.sort(key=lambda x: x['score'], reverse=True)
        for result in chunks_from_rag:
            print("Content:", result['content'])
            # print("Metadata:", result['metadata'])
            print("Similarity Score:", result['score'])

        chunks_from_rag.extend(results[:5])

        # Now send top five Chunks to LLM
        llm_chatbot: Chatbot = Chatbot()
        final_query_for_llm = " ".join(query_top['content'] for query_top in chunks_from_rag)

        context = '''You are a helpful financial assistant. Make sure the response is concise and to the point what is asked
            make sure 90% of the contents in the response should be from the context being passed in'''
        llm_chatbot.set_system_context(context)
        # Perform a search
        # query = "Mid-Size advisers large size advisers tell me more what is difference between mid, small and large size advisers in dollar terms"
        llm_response = llm_chatbot.chat(final_query_for_llm, revisedQuery=False)
        # final_llm_result.extend(response[-1]['content']['content'])
        for rr in llm_response:
            if rr.get('role') == 'assistant':
                final_llm_contents = rr['content']['content']

        print(final_llm_contents)
        return final_llm_contents
