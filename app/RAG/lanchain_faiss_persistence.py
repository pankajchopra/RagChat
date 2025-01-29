import tensorflow_hub as hub
import tensorflow as tf
from typing import List, Optional, Any, Dict
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
import numpy as np
import pickle
import os
import faiss


class UniversalSentenceEncoder(Embeddings):
    """
    LangChain wrapper for Universal Sentence Encoder with local model support
    """

    def __init__(self, model_path: str):
        """
        Initialize the Universal Sentence Encoder from a local path
        """
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model path does not exist: {model_path}")
            self.model = hub.load(model_path)
        except Exception as e:
            raise Exception(f"Failed to load Universal Sentence Encoder from {model_path}: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        if not texts:
            return []
        try:
            batch_size = 32
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.model(batch)
                embeddings.extend(batch_embeddings.numpy().tolist())
            return embeddings
        except Exception as e:
            raise Exception(f"Error during document embedding: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        try:
            embedding = self.model([text])
            return embedding.numpy().tolist()[0]
        except Exception as e:
            raise Exception(f"Error during query embedding: {str(e)}")


class LangchainFAISSIndexManager:
    """
    A class to manage FAISS vector store operations using LangChain.
    """

    def __init__(self, model_path: str):
        """Initialize with local Universal Sentence Encoder"""
        self.model_path = model_path
        self.embedding_model = UniversalSentenceEncoder(model_path)
        self.index: Optional[FAISS] = None
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

    def create_index(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Create a new FAISS index from texts"""
        try:
            if not texts:
                raise ValueError("No texts provided for indexing")

            # Store original texts and metadata
            self.texts = texts
            self.metadatas = metadatas if metadatas else [{} for _ in texts]

            # Create chunks if text is too long
            max_sequence_length = 512  # USE limit
            chunked_texts = []
            chunked_metadata = []

            for i, text in enumerate(texts):
                if len(text.split()) > max_sequence_length:
                    words = text.split()
                    chunks = [' '.join(words[j:j + max_sequence_length])
                              for j in range(0, len(words), max_sequence_length)]
                    chunked_texts.extend(chunks)

                    if metadatas:
                        chunked_metadata.extend([metadatas[i]] * len(chunks))
                else:
                    chunked_texts.append(text)
                    if metadatas:
                        chunked_metadata.append(metadatas[i])

            # Create the index
            self.index = FAISS.from_texts(
                texts=chunked_texts,
                embedding=self.embedding_model,
                metadatas=metadatas
            )
        except Exception as e:
            raise Exception(f"Failed to create index: {str(e)}")

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add additional texts to existing index"""
        if self.index is None:
            raise ValueError("No index exists. Create an index first using create_index()")

        try:
            # Update stored texts and metadata
            self.texts.extend(texts)
            new_metadatas = metadatas if metadatas else [{} for _ in texts]
            self.metadatas.extend(new_metadatas)

            # Add to index
            self.index.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            raise Exception(f"Failed to add texts to index: {str(e)}")

    def save_index(self, directory: str, index_name: str) -> None:
        """
        Save the FAISS index and associated data to disk.
        """
        if self.index is None:
            raise ValueError("No index exists to save")

        try:
            os.makedirs(directory, exist_ok=True)

            # Save the raw FAISS index
            faiss_path = os.path.join(directory, f"{index_name}.faiss")
            faiss.write_index(self.index.index, faiss_path)

            # Save the texts and metadata separately
            data = {
                'texts': self.texts,
                'metadatas': self.metadatas
            }
            data_path = os.path.join(directory, f"{index_name}.pkl")
            with open(data_path, 'wb') as f:
                pickle.dump(data, f)

        except Exception as e:
            raise Exception(f"Failed to save index: {str(e)}")


    def save_index_v2(self, directory: str, index_name: str) -> None:
        """
        Save the FAISS index and associated data to disk.
        """
        if self.index is None:
            raise ValueError("No index exists to save")

        try:
            os.makedirs(directory, exist_ok=True)

            # Save the raw FAISS index
            # faiss_path = os.path.join(directory, f"{index_name}.faiss")
            # faiss.write_index(self.index.index, faiss_path)

            self.index.save_local(directory, f"{index_name}")
            # Save the texts and metadata separately
            # data = {
            #     'texts': self.texts,
            #     'metadatas': self.metadatas
            # }
            # data_path = os.path.join(directory, f"{index_name}.pkl")
            # with open(data_path, 'wb') as f:
            #     pickle.dump(data, f)

        except Exception as e:
            raise Exception(f"Failed to save index: {str(e)}")

    def load_index_v2(self, directory: str, index_name: str) -> None:
        self.index = FAISS.load_local(folder_path=directory, index_name="faiss_index", embeddings=self.embedding_model, allow_dangerous_deserialization=True)
    def load_index(self, directory: str, index_name: str) -> None:
        """
        Load the FAISS index and associated data from disk.
        """
        try:
            faiss_path = os.path.join(directory, f"{index_name}.faiss")
            data_path = os.path.join(directory, f"{index_name}.pkl")

            if not os.path.exists(faiss_path) or not os.path.exists(data_path):
                raise FileNotFoundError("Index files not found")

            # Load the raw FAISS index
            faiss_index = faiss.read_index(faiss_path)

            # Load the texts and metadata
            with open(data_path, 'rb') as f:
                data = pickle.load(f)

            self.texts = data['texts']
            self.metadatas = data['metadatas']

            # Create the FAISS wrapper only once
            self.index = FAISS(
                embedding_function=self.embedding_model,
                index=faiss_index,
                docstore=faiss_index.docstore
            )

        except Exception as e:
            raise Exception(f"Failed to load index: {str(e)}")
    def similarity_search(
            self,
            query: str,
            k: int = 4,
            filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search on the index"""
        if self.index is None:
            raise ValueError("No index exists. Create an index first using create_index()")

        try:
            results = self.index.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )

            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                })

            return formatted_results
        except Exception as e:
            raise Exception(f"Failed to perform similarity search: {str(e)}")
