import faiss
import numpy as np
import pickle
from typing import List, Tuple, Dict
import os


class FAISSIndexManager:
    def __init__(self, dimension: int = 512):
        """
        Initialize FAISS index manager
        
        Args:
            dimension: Dimension of vectors to be indexed
        """
        # Initialize standard FAISS index
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)

        # Storage for documents and their metadata
        self.documents = []
        self.metadata = {}

    def add_vectors(self, vectors: np.ndarray, texts: List[str] = None,
                    metadata: List[Dict] = None) -> None:
        """
        Add vectors and associated data to the index
        
        Args:
            vectors: Numpy array of vectors to add
            texts: Optional list of original texts
            metadata: Optional list of metadata dictionaries
        """
        # Store start index for new vectors
        start_idx = len(self.documents)

        # Add vectors to FAISS index
        self.index.add(vectors)

        # Store associated data
        if texts:
            self.documents.extend(texts)

        if metadata:
            for idx, meta in enumerate(metadata, start=start_idx):
                self.metadata[idx] = meta

    def save_index(self, directory: str, prefix: str = "faiss_index") -> None:
        """
        Save FAISS index and associated data
        
        Args:
            directory: Directory to save files
            prefix: Prefix for saved files
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Construct file paths
        index_path = os.path.join(directory, f"{prefix}_index.faiss")
        data_path = os.path.join(directory, f"{prefix}_data.pkl")

        try:
            # Save FAISS index
            faiss.write_index(self.index, index_path)

            # Save associated data
            associated_data = {
                'dimension': self.dimension,
                'documents': self.documents,
                'metadata': self.metadata
            }

            with open(data_path, 'wb') as f:
                pickle.dump(associated_data, f)

            print(f"Successfully saved index to {index_path}")
            print(f"Successfully saved associated data to {data_path}")

        except Exception as e:
            print(f"Error saving index: {str(e)}")
            raise

    @classmethod
    def load_index(cls, directory: str, prefix: str = "faiss_index_index") -> 'FAISSIndexManager':
        """
        Load FAISS index and associated data
        
        Args:
            directory: Directory containing saved files
            prefix: Prefix of saved files
            
        Returns:
            FAISSIndexManager instance with loaded data
        """
        # Construct file paths
        index_path = os.path.join(directory, f"{prefix}_index.faiss")
        data_path = os.path.join(directory, f"{prefix}_data.pkl")

        try:
            # Load associated data first to get dimension
            with open(data_path, 'rb') as f:
                associated_data = pickle.load(f)

            # Create new instance
            instance = cls(dimension=associated_data['dimension'])

            # Load FAISS index
            instance.index = faiss.read_index(index_path)

            # Restore associated data
            instance.documents = associated_data['documents']
            instance.metadata = associated_data['metadata']

            print(f"Successfully loaded index from {index_path}")
            print(f"Successfully loaded associated data from {data_path}")

            return instance

        except Exception as e:
            print(f"Error loading index: {str(e)}")
            raise

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search the index
        
        Args:
            query_vector: Vector to search for
            k: Number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        # Ensure query vector is 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Search the index
        distances, indices = self.index.search(query_vector, k)

        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:  # Valid index
                result = {
                    'index': int(idx),
                    'distance': float(dist),
                    'text': self.documents[idx] if self.documents else None,
                    'metadata': self.metadata.get(idx, {})
                }
                results.append(result)

        return results


# Example usage
if __name__ == "__main__":
    # Create sample data
    dimension = 128
    num_vectors = 1000

    # Generate random vectors for demonstration
    vectors = np.random.random((num_vectors, dimension)).astype('float32')
    texts = [f"Document {i}" for i in range(num_vectors)]
    metadata = [{'id': i, 'category': f"cat_{i % 5}"} for i in range(num_vectors)]

    # Create and populate index
    index_manager = FAISSIndexManager(dimension=dimension)
    index_manager.add_vectors(vectors, texts, metadata)

    # Save index
    save_dir = "faiss_data"
    index_manager.save_index(save_dir, "sample_index")

    # Load index
    loaded_manager = FAISSIndexManager.load_index(save_dir, "sample_index")

    # Perform a search with loaded index
    query_vector = np.random.random(dimension).astype('float32')
    results = loaded_manager.search(query_vector, k=5)

    # Print results
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Index: {result['index']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result['metadata']}")
