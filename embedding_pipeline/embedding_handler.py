from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Union

class EmbeddingHandler:
    """
    Handles embedding generation for various text inputs using Sentence Transformers.
    Uses all-MiniLM-L6-v2 model (384 dimensions) for fast, efficient embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding handler with a pre-trained model.
        
        Args:
            model_name: Name of the Sentence Transformers model to use
                       - all-MiniLM-L6-v2 (384 dims, fast, recommended)
                       - all-mpnet-base-v2 (768 dims, higher quality)
                       - text-embedding-3-large (3072 dims, requires API)
        """
        print(f"loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"model loaded successfully. embedding dimension: {self.embedding_dim}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        if not text or not isinstance(text, str):
            return np.zeros(self.embedding_dim)
        
        text = text.strip()
        if len(text) == 0:
            return np.zeros(self.embedding_dim)
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        # Filter out empty texts
        texts = [t.strip() if isinstance(t, str) else "" for t in texts]
        
        if not any(texts):
            return np.zeros((len(texts), self.embedding_dim))
        
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        return embeddings
    
    def combine_fields(self, fields: Dict[str, str], weights: Dict[str, float] = None) -> str:
        """
        Combine multiple text fields for contextual embedding.
        Useful for combining title, description, abstract, etc.
        
        Args:
            fields: Dictionary of field_name: text_content
            weights: Optional dictionary of field_name: weight for repetition
                    (default: equal weight)
            
        Returns:
            Combined text string
        """
        if weights is None:
            weights = {key: 1.0 for key in fields.keys()}
        
        combined_parts = []
        for field_name, text in fields.items():
            if text and isinstance(text, str):
                weight = weights.get(field_name, 1)
                # Repeat text by weight if weight > 1
                if weight > 1:
                    combined_parts.append((field_name + ": " + text + " ") * int(weight))
                else:
                    combined_parts.append(f"{field_name}: {text} ")
        
        return "".join(combined_parts).strip()
    
    def get_embedding_info(self) -> Dict:
        """
        Get information about the embedding model.
        
        Returns:
            Dictionary with model info
        """
        return {
            "model_name": self.model.modules()[0].auto_model.config.model_type if hasattr(self.model, 'modules') else "unknown",
            "embedding_dimension": self.embedding_dim,
            "max_seq_length": self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else None
        }


# Test if run directly
if __name__ == "__main__":
    print("\ntesting embedding handler...")
    print("="*80)
    
    handler = EmbeddingHandler()
    info = handler.get_embedding_info()
    print(f"\nmodel info: {info}")
    
    # Test single embedding
    test_text = "This is a sample text about AI and machine learning in Python"
    embedding = handler.embed_text(test_text)
    print(f"\nsingle embedding shape: {embedding.shape}")
    print(f"sample embedding (first 5 dims): {embedding[:5]}")
    
    # Test batch embedding
    test_texts = [
        "Machine learning framework for NLP",
        "Distributed computing with Python",
        "Web development with Django"
    ]
    batch_embeddings = handler.embed_batch(test_texts)
    print(f"\nbatch embeddings shape: {batch_embeddings.shape}")
    
    # Test combined fields
    combined_text = handler.combine_fields({
        "title": "AI Framework",
        "description": "A powerful machine learning library",
        "abstract": "For neural networks"
    }, weights={"title": 2, "description": 1, "abstract": 1})
    
    combined_embedding = handler.embed_text(combined_text)
    print(f"\ncombined text: {combined_text}")
    print(f"combined embedding shape: {combined_embedding.shape}")
    
    print("\n" + "="*80)
    print("all tests passed successfully!")
