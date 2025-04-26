import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.log import logger
import glob

# File paths
DATA_DIR = "llm/data/files"
INDEX_DIR = "llm/data"

class DataPipeline:
    def __init__(self, data_dir: str = DATA_DIR):
        """Initialize the data pipeline with the data directory."""
        self.data_dir = data_dir
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.documents = []
        self.metadata = []
        self.index = None

    def load_text_file(self, filename: str):
        """Load and chunk a single text file."""
        self.documents = []
        self.metadata = []
        
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist.")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking: split by double newlines (paragraphs)
            chunks = content.split('\n\n')
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Ignore empty chunks
                    self.documents.append(chunk.strip())
                    self.metadata.append({
                        'source': filename,
                        'chunk_id': i
                    })
            logger.info(f"Processed {filename} with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            raise
        
        if not self.documents:
            raise ValueError(f"No valid content found in {filename}")

    def generate_embeddings(self):
        """Generate embeddings for all documents."""
        if not self.documents:
            raise ValueError("No documents loaded. Run load_text_file() first.")
        
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(self.documents, show_progress_bar=True)
        logger.info("Embeddings generated")
        return np.array(embeddings).astype('float32')

    def build_faiss_index(self, dataset_id: str, force_rebuild: bool = False):
        """Build or load FAISS index for a specific dataset."""
        faiss_index_path = os.path.join(INDEX_DIR, f"faiss_index_{dataset_id}.pkl")
        metadata_path = os.path.join(INDEX_DIR, f"metadata_{dataset_id}.pkl")
        
        if not force_rebuild and os.path.exists(faiss_index_path) and os.path.exists(metadata_path):
            # Load existing FAISS index and metadata
            with open(faiss_index_path, 'rb') as f:
                self.index = pickle.load(f)
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            self.documents = [meta['text'] for meta in self.metadata]
            logger.info(f"Loaded existing FAISS index and metadata from {faiss_index_path}")
        else:
            # Generate embeddings
            embedding_matrix = self.generate_embeddings()

            # Build FAISS index
            self.index = faiss.IndexFlatL2(embedding_matrix.shape[1])
            self.index.add(embedding_matrix)
            logger.info(f"FAISS index built with {len(self.documents)} vectors")

            # Update metadata with text content
            for i, doc in enumerate(self.documents):
                self.metadata[i]['text'] = doc

            # Save FAISS index and metadata
            os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
            with open(faiss_index_path, 'wb') as f:
                pickle.dump(self.index, f)
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved FAISS index to {faiss_index_path} and metadata to {metadata_path}")

    def get_index_and_metadata(self, dataset_id: str, filename: str, force_rebuild: bool = False):
        """Return the FAISS index, documents, and metadata for a specific dataset."""
        if self.index is None or not self.documents or force_rebuild:
            self.load_text_file(filename)
            self.build_faiss_index(dataset_id, force_rebuild)
        return self.index, self.documents, self.metadata

    @staticmethod
    def list_existing_indices(index_dir: str = INDEX_DIR):
        """List all existing FAISS index files in the index directory."""
        index_files = glob.glob(os.path.join(index_dir, "faiss_index_*.pkl"))
        indices = [os.path.basename(f).replace("faiss_index_", "").replace(".pkl", "") for f in index_files]
        return indices

if __name__ == "__main__":
    """Process all .txt files in llm/data/files and build FAISS indices."""
    try:
        pipeline = DataPipeline()
        existing_indices = pipeline.list_existing_indices()
        
        # Process each .txt file
        txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
        if not txt_files:
            raise ValueError(f"No .txt files found in {DATA_DIR}")

        for txt_file in txt_files:
            dataset_id = os.path.splitext(txt_file)[0]  # e.g., "common_home_network_problems"
            if dataset_id in existing_indices:
                logger.info(f"Index for {dataset_id} already exists, skipping unless forced")
                print(f"Index for {dataset_id} exists. Run with force_rebuild=True to overwrite.")
                continue
            
            logger.info(f"Processing {txt_file} with dataset_id: {dataset_id}")
            pipeline.load_text_file(txt_file)
            pipeline.build_faiss_index(dataset_id, force_rebuild=False)
            print(f"Created FAISS index for {dataset_id}")

        logger.info("Data pipeline completed successfully")
        print("Data pipeline completed. Indices saved in llm/data/")
    except Exception as e:
        logger.error(f"Data pipeline failed: {str(e)}")
        print(f"Error: {str(e)}")