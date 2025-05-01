import ollama
from llm.data.data_pipeline import DataPipeline
from sentence_transformers import SentenceTransformer
from utils.log import logger
import numpy as np
import re

class RagAgent:
    def __init__(self, decider_model: str = "gemma3"):
        """Initialize the RagAgent with data pipeline and embedding model."""
        self.pipeline = DataPipeline()
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.decider_model = decider_model
        self.index = None
        self.documents = []
        self.metadata = []
        
        # define tool-specific query prefixes for contextual retrieval
        self.tool_prefixes = {
            "check_common_issues": "ortak ağ sorunları: ",
            "check_router_troubleshooting": "yönlendirici sorun giderme: "
        }
        
        # map tools to dataset_ids
        self.tool_to_dataset = {
            "check_common_issues": "common_home_network_problems",
            "check_router_troubleshooting": "network_troubleshooting"
        }

    def select_dataset(self, query: str, selected_tool: str = None) -> tuple[str, str]:
        """
        Select the dataset_id and tool_name based on the query and selected tool.
        Used by local LLMs
        """
        available_datasets = self.pipeline.list_existing_indices()
        if not available_datasets:
            logger.error("No FAISS indices available")
            raise ValueError("No FAISS indices found in llm/data")

        # check if selected_tool maps directly to a dataset
        if selected_tool and selected_tool in self.tool_to_dataset:
            dataset_id = self.tool_to_dataset[selected_tool]
            if dataset_id in available_datasets:
                logger.info(f"Selected dataset_id {dataset_id} based on tool {selected_tool}")
                return dataset_id, selected_tool

        # fallback to for query-based selection
        dataset_options = ", ".join(available_datasets)
        tool_options = ", ".join(self.tool_prefixes.keys())
        prompt = f"""
        Kullanıcı sorusu: {query}
        Mevcut veri setleri: {dataset_options}
        Mevcut araçlar: {tool_options}
        Soru hangi veri seti ve araçla en alakalı? Yanıtı TAM OLARAK şu formatta döndür:
        dataset: <dataset_id>
        tool: <tool_name>
        Örnek:
        dataset: common_home_network_problems
        tool: check_common_issues
        Yalnızca bu formatta yanıt ver, başka metin ekleme.
        """
        
        response = ollama.chat(
            model=self.decider_model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        
        # parse the response
        selected_dataset = None
        selected_tool = None
        response_text = response["message"].get("content", "").strip()
        
        # extract dataset and tool
        dataset_match = re.search(r"dataset:\s*(\S+)", response_text)
        tool_match = re.search(r"tool:\s*(\S+)", response_text)
        
        if dataset_match and tool_match:
            selected_dataset = dataset_match.group(1)
            selected_tool = tool_match.group(1)
        
        # validate
        if selected_dataset in available_datasets and selected_tool in self.tool_prefixes:
            logger.info(f"Selected dataset_id {selected_dataset} and tool {selected_tool} based on query")
            return selected_dataset, selected_tool
        else:
            # fallback to available datasets
            logger.warning(f"Invalid selection (dataset: {selected_dataset}, tool: {selected_tool}), using fallback")
            for tool, dataset in self.tool_to_dataset.items():
                if dataset in available_datasets:
                    logger.info(f"Fallback to dataset_id {dataset} and tool {tool}")
                    return dataset, tool
            # last fallback
            logger.info(f"Ultimate fallback to dataset_id {available_datasets[0]} and tool check_common_issues")
            return available_datasets[0], "check_common_issues"

    async def call_rag_tool(self, tool_name: str, query: str, dataset_id: str, k: int = 3) -> str:
        """Call the RAG tool to retrieve relevant information based on tool_name, query, and dataset_id."""
        if tool_name not in self.tool_prefixes:
            logger.info(f"Tool {tool_name} does not require RAG, skipping retrieval")
            return "İlgili bilgi bulunamadı."  # No RAG for non-troubleshooting tools
        
        logger.info(f"Calling RAG tool: {tool_name} with query: {query} using dataset: {dataset_id}")
        
        # load the FAISS index for the selected dataset
        filename = f"{dataset_id}.txt" 
        self.index, self.documents, self.metadata = self.pipeline.get_index_and_metadata(dataset_id, filename)
        
        # get the prefix for the tool to bias retrieval
        prefix = self.tool_prefixes.get(tool_name, "")
        modified_query = prefix + query

        # generate embedding for the modified query
        query_embedding = self.embedding_model.encode([modified_query])[0]

        # search FAISS index for top-k similar documents
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k)
        
        # filter results based on tool_name for relevance
        relevant_chunks = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                # Bias towards relevant files
                if (tool_name == "check_common_issues" and "common_home_network_problems" in meta['source']) or \
                   (tool_name == "check_router_troubleshooting" and "network_troubleshooting" in meta['source']):
                    relevant_chunks.append(self.documents[idx])
                elif tool_name not in self.tool_prefixes:  # Fallback for generic queries
                    relevant_chunks.append(self.documents[idx])
        
        # format retrieved information
        if relevant_chunks:
            retrieved_info = "\n\n".join(relevant_chunks)
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for {tool_name} from {dataset_id}")
            logger.info(f"Retrieved information: \n{retrieved_info}")
        else:
            retrieved_info = "İlgili bilgi bulunamadı."  # No relevant information found
            logger.info(f"No relevant chunks found for {tool_name} in {dataset_id}")

        return retrieved_info