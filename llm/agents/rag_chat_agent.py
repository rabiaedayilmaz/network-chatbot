import faiss
import pandas as pd
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer


DATA_PATH = "llm/utils/data/shm_listesi.csv"
FAISS_INDEX_PATH = "llm/utils/data/faiss_index.pkl"


def generate_embeddings(text_list):
    """Generates all-MiniLM-L6-v2 embeddings for a list of texts."""
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(text_list)
    return embeddings.tolist()

def initialize_faiss():
    """Loads or builds the FAISS index."""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(DATA_PATH):
        # Load existing FAISS index and dataset
        with open(FAISS_INDEX_PATH, "rb") as f:
            index = pickle.load(f)
        df = pd.read_csv(DATA_PATH)
    else:
        # scrape and process the data
        scrape_sym(URL)
        df = pd.read_csv(DATA_PATH)

        if "name" not in df.columns or "address" not in df.columns:
            raise ValueError("CSV file is missing required columns: name, address")

        # generate embeddings
        df["embedding"] = generate_embeddings(df["name"].astype(str).tolist())

        # convert embeddings to np array
        embedding_matrix = np.array(df["embedding"].tolist()).astype("float32")

        # build faiss index
        index = faiss.IndexFlatL2(embedding_matrix.shape[1])
        index.add(embedding_matrix)

        # save faiss index
        with open(FAISS_INDEX_PATH, "wb") as f:
            pickle.dump(index, f)
        
        # save processed dataset
        df.to_csv(DATA_PATH, index=False)

    return df, index

# Load embedding model
embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cuda"}
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs=model_kwargs
)

# Create FAISS vector store
vectorstore = FAISS.from_documents(docs, embeddings)

# Save and reload the vector store
vectorstore.save_local("faiss_index_")
persisted_vectorstore = FAISS.load_local("faiss_index_", embeddings, allow_dangerous_deserialization=True)

# Create a retriever
retriever = persisted_vectorstore.as_retriever()